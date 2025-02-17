from chatbot.chat_bot import ChatBot, ChatBotResponse
from chatbot.models import ServiceClient


class ServiceClientChatBot(ChatBot):
    command_prefix = "client"

    @classmethod
    def handle_command(cls, command_string: str, phone_number: str) -> ChatBotResponse:
        # Check if the command starts with the client prefix
        if command_string.lower().startswith(f"{cls.command_prefix} name "):
            return cls._handle_client_name(command_string, phone_number)
        elif command_string.lower().startswith(f"{cls.command_prefix} email "):
            return cls._handle_client_email(command_string, phone_number)

        return ChatBotResponse(
            "❌ Invalid command. Use 'client name <full_name>' or 'client email <email>' to update client information.")

    @classmethod
    def _handle_client_name(cls, command_string: str, phone_number: str) -> ChatBotResponse:
        # Extract name from the command
        name = command_string[len("client name "):].strip()

        if not name:
            return ChatBotResponse("❌ Name cannot be empty. Please provide a valid name.")

        # Check if the client already exists
        client, created = ServiceClient.objects.get_or_create(phone_number=phone_number)

        # Update name if the client exists
        client.name = name
        client.save()

        if created:
            return ChatBotResponse(f"✅ New client created with name: {name}.")
        else:
            return ChatBotResponse(f"✅ Client's name updated to: {name}.")

    @classmethod
    def _handle_client_email(cls, command_string: str, phone_number: str) -> ChatBotResponse:
        # Extract email from the command
        email = command_string[len("client email "):].strip()

        if not email:
            return ChatBotResponse("❌ Email cannot be empty. Please provide a valid email.")

        # Check if the client already exists
        client, created = ServiceClient.objects.get_or_create(phone_number=phone_number)

        # Update email if the client exists
        client.email = email
        client.save()

        if created:
            return ChatBotResponse(f"✅ New client created with email: {email}.")
        else:
            return ChatBotResponse(f"✅ Client's email updated to: {email}.")
