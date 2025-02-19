import os
import sendgrid
from sendgrid import Email
from sendgrid.helpers.mail import Content, Mail, Category, CustomArg

import boto3
from botocore.exceptions import ClientError

from atila.settings import ATILA_STAGE
from atila.utils import validate_substituted_variables
import logging

from python_http_client.exceptions import HTTPError

sqs_client = boto3.client("sqs", region_name="us-east-1")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def send_email_sendgrid(email_data: dict):
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    if not SENDGRID_API_KEY:
        logger.error("SENDGRID_API_KEY is not set. Emails will not be sent.")
        return {'status_code': 500, 'error': 'Missing SENDGRID_API_KEY'}

    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    from_email = Email(email_data['from_email'], email_data.get('from_email_name'))
    to_email = Email(email_data['to_email'], email_data.get('to_email_name'))
    subject = email_data['subject']
    email_html = email_data['body']

    content = Content("text/html", email_html)
    sendgrid_mail = Mail(from_email, subject, to_email, content)

    if email_data.get('bcc_email'):
        sendgrid_mail.personalizations[0].add_bcc(Email(email_data['bcc_email']))

    if email_data.get('template_id'):
        sendgrid_mail.template_id = "85802dc2-a422-4e70-b1a5-fe76b3fd941b"

    email_data.setdefault('custom_arg', {})
    email_data['custom_arg'].update({'atila_stage': ATILA_STAGE, 'subject': subject})

    for key, value in email_data['custom_arg'].items():
        sendgrid_mail.add_custom_arg(CustomArg(key, value))

    sendgrid_mail.add_category(Category(ATILA_STAGE))
    if email_data.get('category'):
        for category in email_data['category']:
            sendgrid_mail.add_category(Category(category))

    try:
        logger.info(f"Sending email via SendGrid: {email_data}")
        response = sg.client.mail.send.post(request_body=sendgrid_mail.get())
        logger.info(f"SendGrid Response: {response.status_code}")
        return {'status_code': response.status_code}
    except HTTPError as e:
        logger.error(f"SendGrid HTTPError: {str(e)}")
        return {'status_code': 500, 'error': str(e)}


def send_email_ses(email_data: dict):
    AWS_REGION = "us-east-1"
    client = boto3.client('ses', region_name=AWS_REGION)
    sender = f"{email_data.get('from_email_name', '')} <{email_data['from_email']}>"
    destination = {'ToAddresses': [email_data['to_email']]}

    if email_data.get('bcc_email'):
        destination['BccAddresses'] = email_data['bcc_email'] if isinstance(email_data['bcc_email'], list) else [
            email_data['bcc_email']]
    if email_data.get('cc_email'):
        destination['CcAddresses'] = email_data['cc_email'] if isinstance(email_data['cc_email'], list) else [
            email_data['cc_email']]

    subject = email_data['subject']
    body_html = email_data['body']
    email_data.setdefault('custom_arg', {})
    email_data['custom_arg'].update({'atila_stage': ATILA_STAGE, 'subject': subject})

    email_tags = [{'Name': key.replace("@", "__at__").replace(".", "_"),
                   'Value': str(value).replace("@", "__at__").replace(".", "_")}
                  for key, value in email_data['custom_arg'].items() if " " not in str(value)]

    reply_to_emails = email_data.get('reply_to', [])
    reply_to_emails = [reply_to_emails] if isinstance(reply_to_emails, str) else reply_to_emails

    try:
        response = client.send_email(
            Destination=destination,
            Message={'Body': {'Html': {'Charset': "UTF-8", 'Data': body_html}},
                     'Subject': {'Charset': "UTF-8", 'Data': subject}},
            Source=sender,
            Tags=email_tags,
            ReplyToAddresses=reply_to_emails,
        )
        logger.info(f"SES Email sent! Message ID: {response['MessageId']}")
        return {'message_id': response['MessageId'], 'status_code': response['ResponseMetadata']['HTTPStatusCode']}
    except ClientError as e:
        logger.error(f"SES Error: {e.response['Error']['Message']}")
        return {'status_code': e.response['ResponseMetadata']['HTTPStatusCode'],
                'error': e.response['Error']['Message']}


def send_email(email_data: dict, email_provider='sendgrid', validate_substitutions=True):
    to_email = email_data.get("to_email")

    if validate_substitutions:
        validate_substituted_variables(email_data["body"])

    if ATILA_STAGE in ["dev", "staging"]:
        email_data["subject"] = f"[{ATILA_STAGE}] {email_data['subject']}"

    if "@hotmail" in to_email or "@live" in to_email or "@outlook" in to_email:
        logger.warning(f"Switching from SendGrid to SES for {to_email}")
        email_provider = "ses"
    elif "@yahoo" in to_email:
        logger.warning(f"Switching from SES to SendGrid for {to_email}")
        email_provider = "sendgrid"

    email_data.setdefault('from_email', 'info@atila.ca')
    email_data.setdefault('from_email_name', 'Atila Tech')

    logger.info(f"Sending email via {email_provider} to {to_email}")
    if email_provider == 'sendgrid':
        return send_email_sendgrid(email_data)
    elif email_provider == 'ses':
        return send_email_ses(email_data)
    else:
        logger.error(f"Invalid email provider: {email_provider}")
        return {'status_code': 400, 'error': 'Invalid email provider'}
