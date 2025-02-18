import json

import stripe
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chatbot.chat_bot_booking import BookingChatBot
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

    @staticmethod
    @api_view(['POST'])
    def handle_stripe_payment_event(request):
        payload = request.body
        try:
            event = stripe.Event.construct_from(
                json.loads(payload), stripe.api_key
            )
        except ValueError as e:
            print(e)
            return Response(status=400)

        # Handle the event
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object  # contains a stripe.PaymentIntent
            email = payment_intent.charges.data[0].billing_details.email
            print("email", email)
            if not email:
                error_message = "No email in payment intent. Cannot link payment to a client"
                print("error_message", error_message)
                print("payment_intent.id", payment_intent.id)
                return Response(data=error_message, status=400)

            response = BookingChatBot.handle_payment_intent_succeeded(payment_intent)
            if response.destination_number:
                send_whatsapp_message(response.text, response.destination_number)
            return Response(response.text, status=response.status)
        else:
            print('Unhandled event type {}'.format(event.type))

        return Response(status=200)
