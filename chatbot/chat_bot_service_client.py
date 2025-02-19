from typing import Optional
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from chatbot.chat_bot import ChatBot, ChatBotResponse
from chatbot.models import ServiceClient


class ServiceClientChatBot(ChatBot):
    command_prefix = "client"

    def __init__(self):
        self.client: Optional[ServiceClient] = None

    def handle_command(self, command_string: str, phone_number: str) -> ChatBotResponse:
        # Retrieve or create the client object
        self.client, created = ServiceClient.objects.get_or_create(phone_number=phone_number)

        # Check for client name or email command
        if command_string.lower().startswith(f"{self.command_prefix} name "):
            return self._handle_client_info(command_string, "name")
        elif command_string.lower().startswith(f"{self.command_prefix} email "):
            return self._handle_client_info(command_string, "email")

        return ChatBotResponse(
            "❌ Invalid command. Use 'client name <full_name>' or 'client email <email>' to update client information.")

    def _handle_client_info(self, command_string: str, field: str) -> ChatBotResponse:
        """Handles both name and email updates for a client."""
        # Extract value from the command
        value = command_string[len(f"{self.command_prefix} {field} "):].strip()

        if not value:
            return ChatBotResponse(f"❌ {field.capitalize()} cannot be empty. Please provide a valid {field}.")

        # Perform specific validation for name (avoid '@' symbol) or email
        if field == "name" and "@" in value:
            return ChatBotResponse("❌ Name cannot contain the '@' symbol. Please provide a valid name.")
        elif field == "email":
            try:
                # Validate email format
                validate_email(value)
            except ValidationError:
                return ChatBotResponse("❌ Invalid email format. Please provide a valid email.")

        # Update the client field dynamically
        try:
            setattr(self.client, field, value)
            self.client.save()
            return ChatBotResponse(f"✅ Client's {field} updated to: {value}.")
        except Exception as e:
            return ChatBotResponse(f"❌ Failed to save client information: {str(e)}.")
