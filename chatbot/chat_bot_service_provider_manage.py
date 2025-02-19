from typing import Optional

from chatbot.models import ServiceProvider, ServiceClient
from chatbot.chat_bot import ChatBotResponse, ChatBot


class ServiceProviderManageChatBot(ChatBot):
    command_prefix = "service"

    COMMANDS = {
        "service create": {
            "pattern": "service create",
            "handler": "_handle_create_service",
            "args_count": 0
        },
        "service edit name": {
            "pattern": "service edit name <service_provider_id> <name>",
            "handler": "_handle_edit_service",
            "field": "name",
            "args_count": 2
        },
        "service edit description": {
            "pattern": "service edit description <service_provider_id> <description>",
            "handler": "_handle_edit_service",
            "field": "description",
            "args_count": 2
        },
        "service edit eventid": {
            "pattern": "service edit eventid <service_provider_id> <eventid>",
            "handler": "_handle_edit_service",
            "field": "cal_com_event_type_id",
            "args_count": 2
        },
        "service edit apikey": {
            "pattern": "service edit apikey <service_provider_id> <apikey>",
            "handler": "_handle_edit_service",
            "field": "cal_com_api_key",
            "args_count": 2
        },
        "service edit help": {
            "pattern": "service edit help",
            "handler": "_handle_edit_help",
            "args_count": 0
        }
    }

    def __init__(self):
        super().__init__()
        self.client: Optional[ServiceClient] = None
        self.current_command: str = ""

    def handle_command(self, command_string: str, phone_number: str) -> ChatBotResponse:
        """Handle incoming command and return appropriate response."""
        self.current_command = command_string.strip()

        # Validate client
        response = self.is_valid_client(phone_number)
        if isinstance(response, ChatBotResponse):
            return response
        self.client = response

        # Split command and validate
        command_parts = self.current_command.split()
        if not command_parts:
            return ChatBotResponse("Empty command.")

        # Extract base command (up to 3 parts for commands like "service edit name")
        base_command = " ".join(command_parts[:3]) if len(command_parts) > 2 else " ".join(command_parts)

        # Find matching command and execute handler
        for cmd, config in self.COMMANDS.items():
            if base_command.startswith(cmd):
                handler = getattr(self, config["handler"], None)
                if not handler:
                    return ChatBotResponse(f"Handler {config['handler']} not implemented.")

                # Extract arguments based on actual command length
                args = command_parts[len(cmd.split()):]
                if len(args) != config.get("args_count", 0):
                    return ChatBotResponse(f"Invalid number of arguments for '{cmd}'.")

                try:
                    return handler(*args)
                except Exception as e:
                    return ChatBotResponse(f"Error processing command: {str(e)}")

        return ChatBotResponse("Invalid command.")

    def _handle_create_service(self) -> ChatBotResponse:
        """Create a new service provider for the client."""
        try:
            service = ServiceProvider.objects.create(client=self.client)
            return ChatBotResponse(f"Service created with ID: {service.id}")
        except Exception as e:
            return ChatBotResponse(f"Error creating service: {str(e)}")

    def _handle_edit_service(self, service_provider_id: str, value: str) -> ChatBotResponse:
        """Edit a service provider field."""
        try:
            field = self._extract_field_from_command()
            if not field:
                return ChatBotResponse("Invalid edit command.")

            service = ServiceProvider.objects.get(
                id=service_provider_id,
                client=self.client
            )
            setattr(service, field, value)
            service.save()
            return ChatBotResponse(f"Service {field} updated successfully.")
        except ServiceProvider.DoesNotExist:
            return ChatBotResponse("Service provider not found.")
        except Exception as e:
            return ChatBotResponse(f"Error updating service: {str(e)}")

    def _handle_edit_help(self) -> ChatBotResponse:
        """Return help text for available commands."""
        commands = "\n".join([
            config["pattern"]
            for cmd, config in self.COMMANDS.items()
            if "edit" in cmd
        ])
        return ChatBotResponse(f"Available commands:\nservice create\n{commands}")

    def _extract_field_from_command(self) -> Optional[str]:
        """Extract the field name from the current command."""
        for cmd, config in self.COMMANDS.items():
            if self.current_command.startswith(cmd) and "field" in config:
                return config["field"]
        return None