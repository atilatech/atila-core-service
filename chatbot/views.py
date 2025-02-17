from rest_framework.decorators import api_view
from rest_framework.response import Response

from chatbot.chat_bot import ChatBotResponse
from chatbot.chat_bot_service_provider import ServiceProviderChatBot
from chatbot.chat_bot_service_client import ServiceClientChatBot
from chatbot.messaging import send_whatsapp_message


class ChatBotViews:

    @staticmethod
    @api_view(['POST'])
    def handle_incoming_message(request):
        command_string = request.data.get('Body').strip()
        incoming_whatsapp_number = request.data.get('WaId')
        print("incoming_whatsapp_number", incoming_whatsapp_number)
        media_url = None
        response = ChatBotResponse()
        if command_string.lower().startswith(ServiceClientChatBot.command_prefix):
            response = ServiceClientChatBot.handle_command(command_string, incoming_whatsapp_number)
        if command_string.lower().startswith(ServiceProviderChatBot.command_prefix):
            response = ServiceProviderChatBot.handle_command(command_string, incoming_whatsapp_number)

        send_whatsapp_message(response.text, incoming_whatsapp_number, media_url)
        return Response({'message': response.text}, status=response.status)
