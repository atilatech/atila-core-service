import stripe

from chatbot.cal_com_service import CalComService
from chatbot.chat_bot import ChatBot, ChatBotResponse
from chatbot.models import ServiceClient, ServiceBooking
from chatbot.credentials import STRIPE_API_KEY


class BookingChatBot(ChatBot):
    STRIPE_API_KEY = STRIPE_API_KEY

    @classmethod
    def handle_command(cls, command_string: str, phone_number: str) -> ChatBotResponse:
        # Check if the command matches the "service book <payment_intent_id>" format
        if command_string.lower().startswith("service search "):
            return cls._handle_service_booking(command_string)

    @classmethod
    def _handle_service_booking(cls, message: str) -> ChatBotResponse:
        payment_intent_id = message[len("service book "):].strip()

        try:
            # Retrieve the PaymentIntent object from Stripe API
            stripe.api_key = cls.STRIPE_API_KEY
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # Check if the PaymentIntent status is "succeeded"
            if payment_intent.status != 'succeeded':
                return ChatBotResponse(
                    text=f"Payment for {payment_intent_id} has not been completed successfully."
                         f" Status: {payment_intent.status}.",
                    http_status=400
                )

            # Call handle_payment_intent_succeeded with the retrieved PaymentIntent
            return cls.handle_payment_intent_succeeded(payment_intent)

        except stripe.ErrorObject.StripeError as e:
            # Handle Stripe API errors
            error_message = f"Stripe error: {str(e)}"
            return ChatBotResponse(text=error_message, http_status=400)

        except Exception as e:
            # Handle any other errors
            error_message = f"An error occurred: {str(e)}"
            return ChatBotResponse(text=error_message, http_status=500)

    @classmethod
    def handle_payment_intent_succeeded(cls, payment_intent: stripe.PaymentIntent) -> ChatBotResponse:
        email = payment_intent.charges.data[0].billing_details.email
        print("email", email)

        # Get the client based on the phone number
        try:
            client: ServiceClient = ServiceClient.objects.get(email=email)
        except ServiceClient.DoesNotExist:
            return ChatBotResponse(text="ServiceClient matching query does not exist.",
                                   http_status=404)

        try:
            # Get the most recently created ServiceBooking for this client where deposit_paid is False
            booking: ServiceBooking = ServiceBooking.objects. \
                filter(client=client, deposit_paid=False).order_by('-date_created').first()

        except ServiceBooking.DoesNotExist:
            return ChatBotResponse(text="No booking found for this user",
                                   http_status=404,
                                   destination_number=client.phone_number)
        if not booking:
            return ChatBotResponse(text="No booking found for this user",
                                   http_status=404,
                                   destination_number=client.phone_number)
        # Save the payment Intent ID to that booking and set deposit_paid=True
        booking.deposit_payment_intent_id = payment_intent.id
        booking.deposit_paid = True
        booking.save()

        # Call delete_reservation to delete the reservation UID
        cal_com_service = CalComService()  # Assuming CalComService is already defined elsewhere
        delete_response = cal_com_service.delete_reservation(booking)
        if delete_response.get("error"):
            error_message = f"Error deleting reservation: {delete_response['error']}"
            return ChatBotResponse(text=error_message, http_status=400,
                                   destination_number=client.phone_number)
        print(f"reservation deleted for {booking}: {booking.reservation_uid}")
        # Call book_a_slot for that ServiceBooking
        book_response = cal_com_service.book_a_slot(booking)
        if book_response.get("error"):
            error_message = f"Error booking slot: {book_response['error']}"
            return ChatBotResponse(text=error_message, http_status=400,
                                   destination_number=client.phone_number)
        # Save the booking ID to the ServiceBooking
        booking.booking_uid = book_response.get('uid')
        print(f"booking completed for {booking}: {booking.booking_uid}")
        booking.save()

        # Send a WhatsApp message to the client confirming the booking
        message = f"Your booking with {booking.provider.name} has been confirmed " \
                  f"for {booking.start_date.strftime('%A, %B %d, %Y %I:%M %p')}"
        return ChatBotResponse(text=message, http_status=201,
                               destination_number=client.phone_number)
