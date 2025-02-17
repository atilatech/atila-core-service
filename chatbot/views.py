from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chatbot.chat_bot import ChatBotResponse
from chatbot.chat_bot_booking import BookingChatBot
from chatbot.messaging import send_whatsapp_message


# Create your views here.

class ChatBotViews:

    @staticmethod
    @api_view(['POST'])
    def handle_incoming_message(request):
        command_string = request.data.get('Body').strip()
        incoming_whatsapp_number = request.data.get('WaId')
        media_url = None
        response = ChatBotResponse()
        if command_string.lower().startswith(BookingChatBot.command_prefix):
            response = BookingChatBot.handle_command(command_string, incoming_whatsapp_number)

        send_whatsapp_message(response, incoming_whatsapp_number, media_url)
        return Response({'message': response}, status=response.status)
