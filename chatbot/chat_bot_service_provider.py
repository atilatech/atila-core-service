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
            elif message.lower().startswith("service book "):
                return cls._handle_service_reservation(message, phone_number)

        return ChatBotResponse(
            "❌ Invalid command. Use 'service search <search_term>', 'service slots <service_provider_id>', "
            "or 'service book <service_provider_id> <slot_index>'.")

    @classmethod
    def _handle_service_reservation(cls, message: str, phone_number: str) -> ChatBotResponse:
        parts = message.split()
        if len(parts) < 4:
            return ChatBotResponse("❌ Invalid command format. Please use: service book <service_provider_id> "
                                   "<slot_index>.")

        service_provider_id = parts[2]
        slot_index = int(parts[3]) - 1

        try:
            provider = ServiceProvider.objects.get(id=service_provider_id)
        except ServiceProvider.objects.DoesNotExist:
            return ChatBotResponse(f"❌ Service provider with ID {service_provider_id} not found.")

        slots = cls.cal_com_service.get_available_slots(provider)
        if isinstance(slots, ChatBotResponse):
            return slots

        if slot_index < 0 or slot_index >= len(slots):
            return ChatBotResponse("❌ Invalid slot index. Please choose a valid slot.")

        selected_slot = slots[slot_index]
        try:
            service_client = ServiceClient.objects.get(phone_number=phone_number)
        except ServiceClient.objects.DoesNotExist:
            return ChatBotResponse("❌ No service client found. Please set your name and email first.", http_status=400)

        if not service_client.name:
            return ChatBotResponse("❌ Please set your name using: client name <full_name>.", http_status=400)
        if not service_client.email:
            return ChatBotResponse("❌ Please set your email using: client email <email>.", http_status=400)

        slot_start = datetime.fromisoformat(selected_slot["start"]).astimezone(pytz.utc)
        service_booking = ServiceBooking.objects.create(client=service_client, provider=provider, start_date=slot_start)
        reservation = cls.cal_com_service.reserve_a_slot(service_booking, slot_start)
        service_booking.reservation_uid = reservation["reservationUid"]
        service_booking.save()
        return ChatBotResponse("❌ Please set your email using: client email <email>.", http_status=400)

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
        except ServiceProvider.objects.DoesNotExist:
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

