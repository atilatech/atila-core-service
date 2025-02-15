import os
import sendgrid
from sendgrid import Email
from sendgrid.helpers.mail import Content, Mail, Category, CustomArg

import boto3
from botocore.exceptions import ClientError

from atila.helpers import validate_substituted_variables
from atila.settings import ATILA_STAGE
import logging

from python_http_client.exceptions import HTTPError

sqs_client = boto3.client("sqs", region_name="us-east-1")

logger = logging.getLogger(__name__)


def send_email_sendgrid(email_data: dict):
    """
    :param email_data: {'bcc_email': str, 'from_email': str,
     'to_email': str, 'subject': str, 'body': str,
      'custom_arg': dict, 'category: list}
    :type email_data: dict
    :return: response
    :rtype: response: str
    """
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    if not SENDGRID_API_KEY:
        print("warning: SENDGRID_API_KEY is not set")
    sg = sendgrid.SendGridAPIClient(apikey=SENDGRID_API_KEY)

    from_email = Email(email_data['from_email'], email_data.get('from_email_name'))
    to_email = Email(email_data['to_email'], email_data.get('to_email_name'))

    subject = email_data['subject']
    email_html = email_data['body']

    content = Content("text/html", email_html)
    sendgrid_mail = Mail(from_email, subject, to_email, content)

    if email_data.get('bcc_email', False):
        sendgrid_mail.personalizations[0].add_bcc(Email(email_data['bcc_email']))

    if email_data.get('template_id', False):
        sendgrid_mail.template_id = "85802dc2-a422-4e70-b1a5-fe76b3fd941b"

    if not email_data.get('custom_arg', False):
        email_data['custom_arg'] = {}

    email_data['custom_arg']['atila_stage'] = ATILA_STAGE
    email_data['custom_arg']['subject'] = subject

    custom_args = email_data['custom_arg']
    for key, value in custom_args.items():
        custom_arg = CustomArg(key, value)
        sendgrid_mail.add_custom_arg(custom_arg)

    sendgrid_mail.add_category(Category(ATILA_STAGE))
    if email_data.get('category', False):
        categories = email_data['category']

        for category in categories:
            sendgrid_mail.add_category(Category(category))

    try:

        print('from_email: {from_email}, to_email: {to_email}, subject: {subject}'.format(**email_data))
        response = sg.client.mail.send.post(request_body=sendgrid_mail.get())
        print('response.status_code:\n', response.status_code)
        response_data = {
            'status_code': response.status_code,
        }
        return response_data
    except HTTPError as http_error:
        print(f"{str(http_error)}: {http_error.to_dict}")
        raise http_error


def send_email_ses(email_data: dict):
    AWS_REGION = "us-east-1"
    client = boto3.client('ses', region_name=AWS_REGION)
    sender = "{} <{}>".format(email_data.get('from_email_name', ''), email_data['from_email'])
    CONFIGURATION_SET = "EmailAnalyticsConfigSet"
    destination = {
        'ToAddresses': [
            email_data['to_email'],
        ],
    }
    if email_data.get('bcc_email'):
        if isinstance(email_data['bcc_email'], str):
            destination['BccAddresses'] = [email_data['bcc_email']]
        else:
            # in this case bcc_email is a list of str (emails).
            destination['BccAddresses'] = email_data['bcc_email']

    if email_data.get('cc_email'):
        if isinstance(email_data['cc_email'], str):
            destination['CcAddresses'] = [email_data['cc_email']]
        else:
            # in this case cc_email is a list of str (emails).
            destination['CcAddresses'] = email_data['cc_email']

    subject = email_data['subject']
    body_html = email_data['body']

    if not email_data.get('custom_arg', False):
        email_data['custom_arg'] = {}

    email_data['custom_arg']['atila_stage'] = ATILA_STAGE
    email_data['custom_arg']['subject'] = subject

    email_tags = []

    reply_to_emails = []
    if email_data.get('reply_to'):
        if isinstance(email_data['reply_to'], str):
            reply_to_emails.append(email_data['reply_to'])
        else:
            reply_to_emails = email_data['reply_to']

    for key, value in email_data['custom_arg'].items():
        # Skip any tags that have spaces in their name. SES tags seems to be meant for simple key, value pairs.
        value = str(value)
        if " " in value:
            continue
        # In case an email is passed as a tag name or value
        # e.g. Invalid tag value <bsmith@ldcsb.ca>: only alphanumeric ASCII characters, '_', and '-' are allowed.
        value = value.replace("@", "__at__")
        value = value.replace(".", "_")

        key = key.replace("@", "__at__")
        key = key.replace(".", "_")
        tag = {
            'Name': key,
            'Value': value
        }
        email_tags.append(tag)

    charset = "UTF-8"
    try:
        response = client.send_email(
            Destination=destination,
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
            Tags=email_tags,
            ConfigurationSetName=CONFIGURATION_SET,
            ReplyToAddresses=reply_to_emails,
        )
        print("Email sent! Message ID:"),
        print(response['MessageId'])
        print('from_email: {from_email}, to_email: {to_email}, subject: {subject}'.format(**email_data))

        response_data = {
            'message_id': response['MessageId'],
            'status_code': response['ResponseMetadata']['HTTPStatusCode'],
        }
        return response_data
    except ClientError as e:
        print("send_email_ses Exception")
        print(e.response['Error']['Message'])
        print('status_code', e.response['ResponseMetadata']['HTTPStatusCode'])

        raise e

    # TODO use this in a test


def send_email(email_data: dict, email_provider='sendgrid', validate_substitutions=True):
    """
    :param email_data: {'from_email': str,
                         'to_email': str,
                         'subject': str,
                         'body': str,
                         'custom_arg': dict,
                         'category': list,
                         'cc_email': str | list of str, (cc_email is SES ONLY currently)
                         'bcc_email': str | list of str, (list of str format is SES only currently)
                         'reply_to': str | list of str, (reply_to is SES ONLY currently)}

    :param email_data: dict
    :param email_provider: ['sendgrid', 'ses']
    :param email_provider: str
    :param queue_email: bool
    :param validate_substitutions: bool
    :return:
    :rtype:
    """

    to_email = email_data["to_email"]

    if validate_substitutions:
        validate_substituted_variables(email_data["body"])

    if ATILA_STAGE in ["dev", "staging"]:
        email_data["subject"] = f"[{ATILA_STAGE}] {email_data['subject']}"
    # Hotmail, Live, and Outlook email servers are blocking our emails sent via sendgrid
    # see: https://github.com/ademidun/atila-django/issues/183
    if any(blocked_domain in to_email for blocked_domain in ["@hotmail", "@live", "@outlook"]) \
            and email_provider == "sendgrid":
        print("Potential problematic Email domain name found.")
        print(f"Email: {to_email}. Domain: {to_email.split('@')[1]}.\n"
              f"Switching email provider from sendgrid to ses. "
              f"See: https://github.com/ademidun/atila-django/issues/183")
        email_provider = "ses"

    if any(blocked_domain in to_email for blocked_domain in ["@yahoo"]) \
            and email_provider == "ses":
        print("Potential problematic Email domain name found.")
        print(f"Email: {to_email}. Domain: {to_email.split('@')[1]}.\n"
              f"Switching email provider from ses to sendgrid."
              f"See: https://github.com/ademidun/atila-django/issues/183#issuecomment-726727170")
        email_provider = "sendgrid"

    if email_data.get('bcc_email'):
        print(f"send_email_{email_provider}() using bcc_email: {email_data['bcc_email']}")

    if not email_data.get('from_email'):
        email_data['from_email'] = 'info@atila.ca'
        email_data['from_email_name'] = 'Atila Tech'

    elif email_provider == 'sendgrid':
        return send_email_sendgrid(email_data)
    elif email_provider == 'ses':
        return send_email_ses(email_data)
