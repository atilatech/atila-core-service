from datetime import datetime, timedelta

import pytz
import requests
from django.db.models import Q
from chatbot.chat_bot import ChatBot, ChatBotResponse
from chatbot.models import ServiceProvider, ServiceClient


class ServiceProviderChatBot(ChatBot):
    command_prefix = "service"

    @classmethod
    def handle_command(cls, message: str, phone_number: str) -> ChatBotResponse:
        # Check if the message starts with the command prefix
        if message.lower().startswith(f"{cls.command_prefix} "):
            if message.lower().startswith("service search "):
                return cls._handle_service_search(message)
            elif message.lower().startswith("service slots "):
                return cls._handle_service_slots(message)
            elif message.lower().startswith("service book "):
                return cls._handle_service_booking(message, phone_number)

        return ChatBotResponse(
            "❌ Invalid command. Use 'service search <search_term>', 'service slots <service_provider_id>', "
            "or 'service book <service_provider_id> <slot_index>'.")

    @classmethod
    def _handle_service_booking(cls, message: str, phone_number: str) -> ChatBotResponse:
        parts = message.split()

        # Validate command format
        if len(parts) < 4:
            return ChatBotResponse(
                "❌ Invalid command format. Please use: service book <service_provider_id> <slot_index>.")

        service_provider_id = parts[2]
        slot_index = int(parts[3]) - 1  # Convert to zero-based index

        # Attempt to retrieve the service provider
        try:
            provider = ServiceProvider.objects.get(id=service_provider_id)
        except ServiceProvider.objects.DoesNotExist:
            return ChatBotResponse(
                f"❌ Service provider with ID {service_provider_id} not found. Please check the ID and try again.")

        # Get current date and date 7 days later for fetching availability
        current_date = datetime.now().date()
        end_date = current_date + timedelta(days=7)

        # Prepare API request to get available slots
        slots_url = "https://api.cal.com/v2/slots"
        querystring = {
            "start": current_date.isoformat(),  # Current date in ISO format
            "end": end_date.isoformat(),  # Date 7 days from now
            "eventTypeSlug": provider.cal_com_event_type_slug,
            "username": provider.cal_com_username,
            "timeZone": "America/Toronto"
        }
        headers = {
            "Authorization": f"Bearer {provider.cal_com_api_key}",
            "cal-api-version": "2024-09-04"
        }

        # Send request to Cal.com API
        try:
            response = requests.get(slots_url, headers=headers, params=querystring)
        except requests.exceptions.RequestException as e:
            return ChatBotResponse(
                f"❌ An error occurred while trying to fetch available slots: {str(e)}. Please try again later.")

        # Check if the API response is successful
        if response.status_code != 200:
            return ChatBotResponse(
                f"❌ Failed to retrieve available slots. Received unexpected status code {response.status_code}. "
                f"Please try again later.")

        # Check if the data is empty
        data = response.json().get("data", {})
        if not data:
            return ChatBotResponse(
                f"❌ No available slots found for the service provider '{provider.name}' within the next 7 days.")

        # Flatten the list of available slots
        slots = []
        for date, slot_list in data.items():
            slots.extend(slot_list)

        # Ensure the requested slot index is within range
        if slot_index < 0 or slot_index >= len(slots):
            return ChatBotResponse(
                f"❌ Invalid slot index. Please choose a valid slot from the available options.")

        # Get the selected slot
        selected_slot = slots[slot_index]

        # Retrieve or prompt for service client details
        try:
            service_client = ServiceClient.objects.get(phone_number=phone_number)
        except ServiceClient.objects.DoesNotExist:
            return ChatBotResponse(
                "❌ No service client found for this phone number. Please provide your name and email first using "
                "'client name <full_name>' and 'client email <email>'.")

        # Ensure service client has name and email
        if not service_client.name:
            return ChatBotResponse(
                "❌ Please set your name using the command: client name <full_name>.")

        if not service_client.email:
            return ChatBotResponse(
                "❌ Please set your email using the command: client email <email>.")

        # Prepare booking details
        slot_start = datetime.fromisoformat(selected_slot["start"])
        # Convert to UTC
        slot_start_utc = slot_start.astimezone(pytz.utc)
        # Format as ISO 8601 string in UTC
        start_iso_8601 = slot_start_utc.isoformat()
        payload = {
            "start": start_iso_8601,
            "eventTypeId": int(provider.cal_com_event_type_id),
            "attendee": {
                "name": service_client.name,
                "email": service_client.email,
                "timeZone": "America/Toronto",
                "phoneNumber": phone_number,
                "language": "en"
            },
        }

        headers = {
            "Authorization": f"Bearer {provider.cal_com_api_key}",  # Use the correct API key
            "cal-api-version": "2024-08-13",
            "Content-Type": "application/json"
        }

        # Send request to create booking
        try:
            bookings_url = "https://api.cal.com/v2/bookings"
            booking_response = requests.post(bookings_url, json=payload, headers=headers)
            if booking_response.status_code == 201:
                dt = slot_start.astimezone(pytz.timezone('America/Toronto'))  # Adjust to desired timezone

                # Format the datetime object into a human-readable string
                human_readable_start_time = dt.strftime("%A, %B %d, %Y %I:%M %p")
                return ChatBotResponse(
                    f"✅ Your booking has been successfully created for {provider.name} "
                    f"on {human_readable_start_time}.")
            else:
                return ChatBotResponse(f"❌ Failed to create booking. {booking_response.text}")
        except requests.exceptions.RequestException as e:
            return ChatBotResponse(
                f"❌ An error occurred while trying to create the booking: {str(e)}. Please try again later.")

    @classmethod
    def _handle_service_search(cls, message: str) -> ChatBotResponse:
        search_term = message[len("service search") + 1:].strip()  # Extract the search term

        # Query ServiceProvider descriptions containing the search term (case-insensitive)
        providers = ServiceProvider.objects.filter(
            Q(description__icontains=search_term)
        )[:5]  # Limit to the top 5 results

        # Format the response for WhatsApp
        if providers:
            response_text = f"*Top Service Providers for '{search_term}':*\n"
            for idx, provider in enumerate(providers, start=1):
                response_text += f"{idx}. *{provider.name}* ({provider.id})\n"
                response_text += f"   {provider.description}\n"
        else:
            response_text = f"❌ No service providers found for '{search_term}'. Try another keyword."

        return ChatBotResponse(response_text)

    @classmethod
    def _handle_service_slots(cls, message: str) -> ChatBotResponse:
        parts = message.split()

        # Check if the command is properly formatted
        if len(parts) < 3:
            return ChatBotResponse("❌ Invalid command format. Please use: service slots <service_provider_id>.")

        service_provider_id = parts[2]

        # Attempt to retrieve the service provider
        try:
            provider = ServiceProvider.objects.get(id=service_provider_id)
        except ServiceProvider.objects.DoesNotExist:
            return ChatBotResponse(
                f"❌ Service provider with ID {service_provider_id} not found. Please check the ID and try again.")

        # Get current date and date 7 days later
        current_date = datetime.now().date()
        end_date = current_date + timedelta(days=7)

        # Prepare API request to get available slots
        url = "https://api.cal.com/v2/slots"
        querystring = {
            "start": current_date.isoformat(),  # Current date in ISO format
            "end": end_date.isoformat(),  # Date 7 days from now
            "eventTypeSlug": provider.cal_com_event_type_slug,
            "username": provider.cal_com_username,
            "timeZone": "America/Toronto"
        }
        headers = {
            "Authorization": f"Bearer {provider.cal_com_api_key}",
            "cal-api-version": "2024-09-04"
        }

        # Send request to Cal.com API and handle potential failure
        try:
            response = requests.get(url, headers=headers, params=querystring)
        except requests.exceptions.RequestException as e:
            return ChatBotResponse(
                f"❌ An error occurred while trying to fetch available slots: {str(e)}. Please try again later.")

        # Check if the API response is successful
        if response.status_code != 200:
            return ChatBotResponse(
                f"❌ Failed to retrieve available slots. Received unexpected status code {response.status_code}. "
                f"Please try again later.")

        # Check if the data is empty
        data = response.json().get("data", {})
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
