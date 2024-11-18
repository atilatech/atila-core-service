from stripe.api_resources.payment_intent import PaymentIntent
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content

from atlas.constants import ATLAS_CREDITS_PER_DOLLAR


def handle_payment_intent_succeeded(payment_intent: PaymentIntent):
    email = payment_intent["charges"]["data"][0]["billing_details"]["email"]
    name = payment_intent["charges"]["data"][0]["billing_details"]["name"]

    # divide by 100 = convert cents into dollars. Multiply by ATLAS_CREDITS_PER_DOLLAR = Convert dollars to credits
    atlas_credits = int(payment_intent["amount_received"] / 100 * ATLAS_CREDITS_PER_DOLLAR)
    send_atlas_credits_email(email, name, atlas_credits)

    pass


def send_atlas_credits_email(to_email, name, atlas_credits):
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("info@atila.ca", "Atila Tech")  # Change to your verified sender
    to_email = To(to_email)  # Change to your recipient
    subject = "Atlas Credits"
    data = {
        "name": name,
        "credits_code": "abc123",
        "atla_credits": atlas_credits,
    }
    email_body = """
    Hey {name},
    <br/><br/>
    Here is the code for your {atla_credits} Atlas credits: {credits_code}
    <br/><br/>
    Visit your profile to add credits to your account: https://atlas.atila.ca/profile
    """.format(**data)

    content = Content("text/html", email_body)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)
