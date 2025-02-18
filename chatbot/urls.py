from django.urls import path
from chatbot.views import ChatBotViews

urlpatterns = [
    path('handle-incoming-message/', ChatBotViews.handle_incoming_message, name='handle_incoming_message'),
    path('handle-stripe-payment-event/', ChatBotViews.handle_stripe_payment_event, name='handle_stripe_payment_event'),
]
