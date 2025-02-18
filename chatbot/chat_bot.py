from abc import ABC, abstractmethod
from typing import Union

from rest_framework import status
from atila.settings import ATILA_STAGE
from chatbot.models import ServiceClient

DEFAULT_CHAT_BOT_RESPONSE = "Invalid command.\n\nPlease type book <search_term> to book a service provider."


class ChatBotResponse:
    def __init__(self, text: str = DEFAULT_CHAT_BOT_RESPONSE,
                 media_url: str = None, http_status: int = status.HTTP_200_OK):
        self.text = text
        self.media_url = media_url
        self.status = http_status


class ChatBot(ABC):
    command_prefix = ""

    @classmethod
    @abstractmethod
    def handle_command(cls, command_string: str, phone_number: str) -> ChatBotResponse:
        """Handle incoming commands and return a ChatBotResponse."""

    @classmethod
    def _is_dev(cls) -> bool:
        """Determine if the app is running in a development environment."""
        return ATILA_STAGE == "dev"

    @classmethod
    def _send_error_message(cls, message: str):
        """Send an error message as a ChatBotResponse."""
        return ChatBotResponse(message, http_status=status.HTTP_400_BAD_REQUEST)
