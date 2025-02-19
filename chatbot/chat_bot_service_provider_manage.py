from typing import Optional

from chatbot.models import ServiceProvider, ServiceClient
from chatbot.chat_bot import ChatBotResponse, ChatBot


class ServiceProviderManageChatBot(ChatBot):
    command_prefix = ["service create", "service edit"]

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
            return ChatBotResponse("Please enter a command. Type 'service edit help' for assistance.")

        # Extract base command (up to 3 parts for commands like "service edit name")
        base_command = " ".join(command_parts[:3]) if len(command_parts) > 2 else " ".join(command_parts)

        # Find matching command and execute handler
        for cmd, config in self.COMMANDS.items():
            if base_command.startswith(cmd):
                handler = getattr(self, config["handler"], None)
                if not handler:
                    return ChatBotResponse(f"Oops! It seems there’s an issue with the command handler."
                                           f" Please try again.")

                # Extract arguments based on actual command length
                args = command_parts[len(cmd.split()):]

                # Handle multi-word descriptions/names
                if config.get("field") in ["name", "description"] and len(args) > 1:
                    # Multi-word case for name/description
                    value = " ".join(args[1:])  # Join all remaining arguments as the field value
                    args = [args[0], value]  # Recreate args with the service provider ID and value
                elif len(args) != config.get("args_count", 0):
                    return ChatBotResponse(f"Invalid number of arguments for '{cmd}'. Make sure to follow the format: "
                                           f"{config['pattern']}")

                try:
                    return handler(*args)
                except Exception as e:
                    return ChatBotResponse(f"Error processing command: {str(e)}."
                                           f" If you're stuck, try 'service edit help' for guidance.")

        return ChatBotResponse("Sorry, I didn’t understand that command. "
                               "Please type 'service edit help' to get a list of available commands.")

    def _handle_create_service(self) -> ChatBotResponse:
        """Create a new service provider for the client."""
        try:
            service = ServiceProvider.objects.create(client=self.client)
            next_steps_help = self._handle_edit_help().text
            return ChatBotResponse(f"Your service has been created successfully! Service ID: {service.id}\n\n"
                                   f"{next_steps_help}")
        except Exception as e:
            return ChatBotResponse(f"Something went wrong while creating the service: {str(e)}. Please try again or "
                                   f"contact support.")

    def _handle_edit_service(self, service_provider_id: str, value: str) -> ChatBotResponse:
        """Edit a service provider field."""
        try:
            field = self._extract_field_from_command()
            if not field:
                return ChatBotResponse("Invalid edit command. Please specify what you want to edit (e.g., name, "
                                       "description).")

            service = ServiceProvider.objects.get(id=service_provider_id)
            setattr(service, field, value)
            service.save()
            return ChatBotResponse(f"Service {field} has been successfully updated to: {value}.")
        except ServiceProvider.DoesNotExist:
            return ChatBotResponse(f"Service provider with ID {service_provider_id} not found. Please check and try "
                                   f"again.")
        except Exception as e:
            return ChatBotResponse(f"Error updating service: {str(e)}. Please ensure your input is correct.")

    def _handle_edit_help(self) -> ChatBotResponse:
        """Return help text for available commands."""
        commands = "\n".join([
            f"• {config['pattern']}"  # Make help more readable
            for cmd, config in self.COMMANDS.items()
            if "edit" in cmd
        ])
        return ChatBotResponse(f"Here are the available commands to manage your service:\n\n"
                               f"{commands}\n\n"
                               f"For step-by-step guidance on setting up your schedule, visit:\n"
                               f"https://info.atila.ca/How-to-Make-a-Cal-Com-Account-1889da443a0e807fadaeff80eaa817e4")

    def _extract_field_from_command(self) -> Optional[str]:
        """Extract the field name from the current command."""
        for cmd, config in self.COMMANDS.items():
            if self.current_command.startswith(cmd) and "field" in config:
                return config["field"]
        return None
