from time import sleep
from twilio.rest import Client

from chatbot.credentials import TWILIO_AUTH_TOKEN, TWILIO_ACCOUNT_SID, WHATSAPP_NUMBER

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    print("Warning: TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN have not been set")
    client = None

TWILIO_CHARACTER_LIMIT = 1000  # Twilio has a 1600 character limit. https://www.twilio.com/docs/errors/21617

SMS_NUMBER = "+19058758867"


def send_whatsapp_message(text, destination_number: str, media_url: str = None, skip_wait: bool = False):
    if not destination_number.startswith('whatsapp:'):
        destination_number = f'whatsapp:{destination_number}'

    destination_number = destination_number.replace(' ', '')
    message = client.messages.create(
        from_=f'whatsapp:{WHATSAPP_NUMBER}',
        body=text[:TWILIO_CHARACTER_LIMIT],
        media_url=media_url,
        to=f'{destination_number}'  # Add your WhatsApp No. here
    )
    print(message.sid)
    if not skip_wait:
        sleep(3)
