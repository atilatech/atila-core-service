from django.db.models import Q
from chatbot.models import ServiceProvider
from chatbot.chat_bot import ChatBot, ChatBotResponse


class BookingChatBot(ChatBot):
    command_prefix = "book"

    @classmethod
    def handle_command(cls, message: str, phone_number: str) -> ChatBotResponse:
        # Check if the message starts with the command prefix
        if message.lower().startswith(f"{cls.command_prefix} "):
            search_term = message[len(cls.command_prefix) + 1:].strip()  # Extract the search term

            # Query ServiceProvider descriptions containing the search term (case-insensitive)
            providers = ServiceProvider.objects.filter(
                Q(description__icontains=search_term)
            )[:5]  # Limit to the top 5 results

            # Format the response for WhatsApp
            if providers:
                response_text = "*Top Service Providers:* 📅\n"
                for idx, provider in enumerate(providers, start=1):
                    response_text += f"{idx}. *{provider.user.name}*\n"  # Adjust if UserProfile has a name field
                    response_text += f"   _{provider.description}_\n"
                    response_text += f"   📅 Booking: {provider.calendar_url}\n\n"
            else:
                response_text = f"❌ No service providers found for '{search_term}'. Try another keyword."

            return ChatBotResponse(response_text)
