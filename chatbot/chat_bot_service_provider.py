from datetime import datetime, timedelta

import requests
from django.db.models import Q

from chatbot.chat_bot import ChatBot, ChatBotResponse
from chatbot.models import ServiceProvider


class ServiceProviderChatBot(ChatBot):
    command_prefix = "service"

    @classmethod
    def handle_command(cls, message: str, phone_number: str) -> ChatBotResponse:
        # Check if the message starts with the command prefix
        if message.lower().startswith(f"{cls.command_prefix} "):
            if message.lower().startswith("service book "):
                return cls._handle_book_service(message)
            elif message.lower().startswith("service search "):
                return cls._handle_service_search(message)

        return ChatBotResponse(
            "❌ Invalid command. Use 'service book <service_provider_id>' or 'service search <search_term>'.")

    @classmethod
    def _handle_book_service(cls, message: str) -> ChatBotResponse:
        parts = message.split()

        # Check if the command is properly formatted
        if len(parts) < 3:
            return ChatBotResponse("❌ Invalid command format. Please use: service book <service_provider_id>.")

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
            print("response.json()", response.json())
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
            response_text += f"\n📆 {date} ({formatted_date}):\n"

            # List all available slots with AM/PM format and continue numbering
            for slot in slots:
                time = datetime.fromisoformat(slot["start"]).strftime("%I:%M %p")  # Convert to AM/PM format
                response_text += f"   {global_slot_index}. 🕒 {time}\n"
                global_slot_index += 1

        return ChatBotResponse(response_text)

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
