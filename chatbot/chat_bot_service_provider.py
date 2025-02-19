import urllib.parse
from datetime import datetime

import pytz
from django.db.models import Q
from rest_framework import status

from chatbot.cal_com_service import CalComService
from chatbot.chat_bot import ChatBot, ChatBotResponse
from chatbot.models import ServiceProvider, ServiceClient, ServiceBooking


class ServiceProviderChatBot(ChatBot):
    command_prefix = "service"

    cal_com_service = CalComService()

    @classmethod
    def handle_command(cls, message: str, phone_number: str) -> ChatBotResponse:
        if message.lower().startswith(f"{cls.command_prefix} "):
            if message.lower().startswith("service search "):
                return cls._handle_service_search(message)
            elif message.lower().startswith("service slots "):
                return cls._handle_service_slots(message)
            elif message.lower().startswith("service reserve "):
                return cls._handle_service_reservation(message, phone_number)

        return ChatBotResponse(
            "❌ Invalid command. Use 'service search <search_term>', 'service slots <service_provider_id>', "
            "or 'service reserve <service_provider_id> <slot_index>'.")

    @classmethod
    def _handle_service_reservation(cls, message: str, phone_number: str) -> ChatBotResponse:
        parts = message.split()
        if len(parts) < 4:
            return ChatBotResponse("❌ Invalid command format. Please use: service reserve <service_provider_id> "
                                   "<slot_index>.")

        service_client, created = ServiceClient.objects.get_or_create(phone_number=phone_number)
        if created:
            return ChatBotResponse("❌ Please set your name and email before reserving a slot,"
                                   " using the following 2 commands\n\n"
                                   "1: client name <full_name>\n\n"
                                   "1: client email <email>",
                                   http_status=400)
        elif not service_client.name:
            return ChatBotResponse("❌ Please set your name using: *client name <full_name>*", http_status=400)
        elif not service_client.email:
            return ChatBotResponse("❌ Please set your email using: *client email <email>.*", http_status=400)

        service_provider_id = parts[2]
        slot_index = int(parts[3]) - 1

        try:
            provider = ServiceProvider.objects.get(id=service_provider_id)
        except ServiceProvider.DoesNotExist:
            return ChatBotResponse(f"❌ Service provider with ID {service_provider_id} not found.")

        slots = cls.cal_com_service.get_available_slots(provider)

        # Flatten the dictionary into a list of slot dictionaries
        slots = [slot for date_slots in slots.values() for slot in date_slots]

        if slot_index < 0 or slot_index >= len(slots):
            return ChatBotResponse("❌ Invalid slot index. Please choose a valid slot.")

        selected_slot = slots[slot_index]["start"]

        slot_start = datetime.fromisoformat(selected_slot).astimezone(pytz.utc)
        service_booking, _ = ServiceBooking.objects.get_or_create(client=service_client,
                                                                  provider=provider,
                                                                  start_date=slot_start)
        reservation = cls.cal_com_service.reserve_a_slot(service_booking)
        print("reservation", reservation)
        service_booking.reservation_uid = reservation["reservationUid"]
        service_booking.save()
        payment_link = cls._get_payment_link(service_client.email)
        if cls.is_dev():
            payment_link += "\n\nTest with 4242424242424242 and any future date and any CVC"

        return ChatBotResponse("🗓 Your reservation has been held for 10 minutes.\n\n"
                               f"💵 Pay the $5 deposit to secure your spot: {payment_link}\n\n"
                               f"✉️ Use {service_client.email} as the email in your payment")

    @classmethod
    def _handle_service_search(cls, message: str) -> ChatBotResponse:
        search_term = message[len("service search") + 1:].strip()
        providers = ServiceProvider.objects.filter(Q(description__icontains=search_term))[:5]
        if providers:
            response_text = f"*Top Service Providers for '{search_term}':*\n"
            for idx, provider in enumerate(providers, start=1):
                response_text += f"{idx}. *{provider.name}* ({provider.id})\n   {provider.description}\n"
        else:
            response_text = f"❌ No service providers found for '{search_term}'."
        return ChatBotResponse(response_text)

    @classmethod
    def _handle_service_slots(cls, message: str) -> ChatBotResponse:
        parts = message.split()
        if len(parts) < 3:
            return ChatBotResponse("❌ Invalid command format. Please use: service slots <service_provider_id>.")

        service_provider_id = parts[2]
        try:
            provider = ServiceProvider.objects.get(id=service_provider_id)
        except ServiceProvider.DoesNotExist:
            return ChatBotResponse(f"❌ Service provider with ID {service_provider_id} not found.")

        data = cls.cal_com_service.get_available_slots(provider)

        if "error" in data:
            return ChatBotResponse(data["error"], http_status=status.HTTP_400_BAD_REQUEST)
        if not data:
            return ChatBotResponse(
                f"❌ No available slots found for the service provider '{provider.name}' within the next 7 days.")

        # Format the available slots response
        response_text = f"📅 *Available Slots for {provider.name}:*\n"

        # Initialize a variable to keep track of the global slot index
        global_slot_index = 1

        for date, slots in data.items():
            # Convert date to day name and format (e.g., Tuesday, February 18)
            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%A, %B %d")
            response_text += f"\n📆 {formatted_date}:\n"

            # List all available slots with AM/PM format and continue numbering
            for slot in slots:
                time = datetime.fromisoformat(slot["start"]).strftime("%I:%M %p")  # Convert to AM/PM format
                response_text += f"   {global_slot_index}. 🕒 {time}\n"
                global_slot_index += 1

        return ChatBotResponse(response_text)

    @classmethod
    def _get_payment_link(cls, prefilled_email=None) -> str:
        """
        Manage Payment Links:
        https://dashboard.stripe.com/test/payment-links/plink_1QtrzoHeg0qPyG6k5XbtLyOv
        https://dashboard.stripe.com/payment-links/plink_1QtdjVHeg0qPyG6kmDWowgtM
        """
        if cls.is_dev():
            payment_link = "https://buy.stripe.com/test_aEU29W7n85andNe8wE"
        else:
            payment_link = "https://buy.stripe.com/5kAdUigIlfdf3VC00f"

        if prefilled_email:
            encoded_email = urllib.parse.quote(prefilled_email)
            payment_link = f"{payment_link}?prefilled_email={encoded_email}"

        return payment_link
