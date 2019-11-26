"""
This file contains utility functions for use in the Pyramid view handling
"""

import datetime
import boto3
from botocore.exceptions import ClientError


def datetime_serializer(obj):
    # datetime.datetime is a subclass of datetime.date, and isinstance returns true if obj is a subclass.
    if isinstance(obj, (datetime.date, datetime.time)):
        return obj.isoformat()
    raise TypeError(f'Type {type(obj)} is not serializable')


def error_dict(error_type='generic_errors', errors=''):
    """
    Create a basic error dictionary for standard use with the intent of being passed to some other outside
    API or whatnot.
    :param type: A plural string without spaces that describes the errors.  Only one type of error should be sent.
    :param errors: A list of error strings describing the problems. A single string will be converted to a single item
    list containing that string.
    :return: A dictionary for the error to be passed.
    """
    if isinstance(errors, str):
        errors = [errors]
    if not isinstance(errors, list):
        raise TypeError('Type for "errors" must be a string or list of strings')
    if not all(isinstance(item, str) for item in errors):
        raise TypeError('Type for "errors" in the list must be a string')
    error = {'error_type': error_type,
             'errors': errors
             }
    return error


def send_email(email, subject, body_text, body_html):
    error = None
    sender = "no-reply@jacob.squizzlezig.com"
    charset = "UTF-8"
    aws_region = "us-west-2"
    client = boto3.client('ses', region_name=aws_region)
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={'ToAddresses': [email]},
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender
        )
    # Return and display an error if something goes wrong.
    except ClientError as e:
        error = error_dict("api_error", e.response["Error"]["Message"])
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

    return error

def send_verification_email(request, user_email, verifytoken, subject = "Please verify your email"):
    verifylink = request.application_url + "/verify?verifytoken=" + verifytoken.token
    body_text = ("Please verify your email by going to " + verifylink + "\r\n"
                "If you did not make this account, please feel free to ignore this email")
    body_html = """
                <html>
                <head></head>
                <body>
                    <p>Please verify your email by going to
                        <a href='""" + verifylink + """'>""" + verifylink + """</a>
                    </p>
                    <p>If you did not make this account, please feel free to ignore this email</p>
                </body>
                </html>
                """
    error = send_email(user_email, subject, body_text, body_html)
    return error

def get_SQS_messages(url):
    client = boto3.client('sqs')
    response = client.receive_message(QueueUrl=url,
                                    AttributeNames=["all"],
                                    MaxNumberOfMessages=10)
    if "Messages" in response:
        return response["Messages"]
    else:
        return None
    
def delete_SQS_messages(url, listOfMessages):
    client = boto3.client('sqs')
    response = client.delete_message_batch(QueueUrl=url,
                                        Entries=listOfMessages)
    if response.get("Failed") is None:
        return "all messages successfully deleted"
    else:
        return "Successfull: " + str(len(response.get("Success"))) + "\n" +\
                "Failed: " +  str(len(response.get("Failed")))

def removeEmailLabelIfAny(email):
    beginningIndex = None
    endingIndex = None
    for charIndex in range(len(email) - 1):
        if email[charIndex] == "+":
            beginningIndex = charIndex
        if beginningIndex is not None and email[charIndex] == "@":
            endingIndex = charIndex
            
    if beginningIndex is not None:
        email = email[0:beginningIndex] + email[endingIndex:]
    
    return email
