from pyramid.response import Response
from pyramid.view import view_config
from pyramid import httpexceptions
import boto3
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from uuid import uuid4
import json

from ..models import UserModel, SessionModel, ResetTokenModel
from ..scripts.password_hashing import pwd_context
from ..scripts.converters import dict_from_row
from ..scripts.utilities import error_dict, datetime_serializer

removals = ['user_pass']

def username_in_use(user_name, dbsession):
    """
    Returns true if a username exists
    :param username: a string username
    :param dbsession: a db session
    :return: True if a username exists, otherwise False
    """
    exists = dbsession.query(UserModel).filter(UserModel.user_name == user_name.lower()).one_or_none()
    return exists is not None


def send_email(email, SUBJECT, BODY_TEXT, BODY_HTML):
    error = None
    SENDER = "no-reply@jacob.squizzlezig.com"
    CHARSET = "UTF-8"
    AWS_REGION = "us-west-2"
    client = boto3.client('ses', region_name=AWS_REGION)
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={'ToAddresses': [email]},
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER
        )
    # Return and display an error if something goes wrong.
    except ClientError as e:
        error = error_dict("api_error", e.response["Error"]["Message"])
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

    return error



# This handles requests without a user_id
@view_config(route_name='users')
def users(request):
    if request.method == 'POST':
        body = request.json_body

        if "user_name" not in body or "user_email" not in body or "user_pass" not in body:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "username, email, and password are required")
        elif username_in_use(body.get('user_name'), request.dbsession):
            status_code = httpexceptions.HTTPConflict.code
            result = error_dict("api_error", "username already in use")
        elif len(body.get("user_pass")) < 8:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "password must be at least 8 characters")
        else:
            status_code = httpexceptions.HTTPOk.code
            user = UserModel()
            user.user_name = body["user_name"].lower()
            user.user_email = body["user_email"].lower()
            user.user_pass = pwd_context.hash(body["user_pass"])
            request.dbsession.add(user)
            # We use flush here so that user has a user_id because we need it for testing
            # Autocommit is true, but just in case that is turned off, we use refresh, so it pulls the user_id
            request.dbsession.flush()
            request.dbsession.refresh(user)

            new_token = str(uuid4())

            s = SessionModel()
            s.user_id = user.user_id
            s.token = new_token
            request.dbsession.add(s)
            request.dbsession.flush()
            request.dbsession.refresh(s)

            result = dict_from_row(user, remove_fields=removals)
            result['session'] = dict_from_row(s, remove_fields=removals)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method == 'PUT':
        body = request.json_body
        if body.get("resettoken"):
            resettoken = request.dbsession.query(ResetTokenModel)\
                .filter(ResetTokenModel.token == body.get("resettoken"))\
                .filter(ResetTokenModel.started > (datetime.utcnow() - timedelta(days=1))).one_or_none()
            if resettoken is None:
                status_code = httpexceptions.HTTPNotFound.code
                result = error_dict("api_error", "reset token doesnt exist")
            elif body.get("user_pass") is None:
                status_code = httpexceptions.HTTPBadRequest.code
                result = error_dict("api_error", "user_pass is required")
            else:
                user = request.dbsession.query(UserModel)\
                    .filter(UserModel.user_id == resettoken.user_id).one_or_none()
                user.user_pass = pwd_context.hash(body.get("user_pass"))
                request.dbsession.delete(resettoken)
                request.dbsession.flush()
                request.dbsession.refresh(user)

                # Set how the email will look
                SUBJECT = "Password successfully reset"
                BODY_TEXT = "Your password was successfully reset"
                BODY_HTML = """
                                <html>
                                <head></head>
                                <body>
                                    <p>Your password was successfully reset</p>
                                </body>
                                </html>
                            """
                error = send_email(user.user_email, SUBJECT, BODY_TEXT, BODY_HTML)
                if error:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error
                else:
                    request.dbsession.query(ResetTokenModel)\
                        .filter(ResetTokenModel.token == body.get("resettoken"))\
                        .filter(ResetTokenModel.started < (datetime.utcnow() - timedelta(days=1))).delete()
                    status_code = httpexceptions.HTTPOk.code
                    result = "password successfully reset"

        elif body.get("user_email") is None:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "user_email is required")
        else:
            user = request.dbsession.query(UserModel)\
                .filter(UserModel.user_email == body.get("user_email").lower()).one_or_none()
            if user is None:
                status_code = httpexceptions.HTTPNotFound.code
                result = error_dict("api_error", "user doesnt exist")
            else:
                # Create and add reset token
                resettoken = ResetTokenModel()
                resettoken.user_id = user.user_id
                resettoken.token = str(uuid4())
                request.dbsession.add(resettoken)
                request.dbsession.flush()
                request.dbsession.refresh(resettoken)

                # Set how the email will look
                resetlink = "jacob.squizzlezig.com/passwordreset?resettoken=" + resettoken.token
                SUBJECT = "Password reset requested"
                BODY_TEXT = ("A password reset was requested\r\n"
                             "If you wish to reset your password, go to " + resetlink + "\r\n"
                             "If you did not request to change your password, feel free to ignore this email"
                             )
                BODY_HTML = """
                <html>
                <head></head>
                <body>
                    <p>A password reset was requested</p>
                    <p>If you wish to reset your password, go to 
                        <a href='""" + resetlink + """'>""" + resetlink + """</a></p>
                    <p>If you did not request to change your password, feel free to ignore this email</p>
                </body>
                </html>
                            """
                error = send_email(user.user_email, SUBJECT, BODY_TEXT, BODY_HTML)
                if error:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error
                else:
                    status_code = httpexceptions.HTTPOk.code
                    result = "email sent"

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )

    if request.method not in ('POST', 'PUT'):
        return Response(status_code=httpexceptions.HTTPMethodNotAllowed.code)


# This handles requests with a user_id
@view_config(route_name='users_by_id')
def users_by_id(request):
    user_id = request.matchdict.get('user_id')
    if request.method == 'GET':
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.code
            result = error_dict("api_error", "not authenticated for this request")
        else:
            if user_id is None or int(user_id) != request.user.user_id:
                status_code = httpexceptions.HTTPUnauthorized.code
                result = error_dict("api_error", "not authenticated for this request")
            else:
                status_code = httpexceptions.HTTPOk.code
                result = dict_from_row(request.user, removals)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method == 'PUT':
        body = request.json_body
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.code
            result = error_dict("api_error", "not authenticated for this request")
        else:
                if user_id is None or int(user_id) != request.user.user_id:
                    status_code = httpexceptions.HTTPUnauthorized.code
                    result = error_dict("api_error", "not authenticated for this request")
                elif body.get("user_name") is None and body.get("user_email") is None and body.get("user_pass") is None:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error_dict("api_error", "no values provided to update")
                else:
                    if body.get("user_name"):
                        request.user.user_name = body.get("user_name").lower()
                    if body.get("user_email"):
                        request.user.user_email = body.get("user_email").lower()
                    if body.get("user_pass"):
                        request.user.user_pass = pwd_context.hash(body.get("user_pass"))

                    request.dbsession.flush()
                    request.dbsession.refresh(request.user)
                    status_code = httpexceptions.HTTPOk.code
                    result = dict_from_row(request.user, remove_fields=removals)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method == 'DELETE':
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.code
            result = error_dict("api_error", "not authenticated for this request")
        else:
            if user_id is None or int(user_id) != request.user.user_id:
                status_code = httpexceptions.HTTPUnauthorized.code
                result = error_dict("api_error", "not authenticated for this request")
            else:
                status_code = httpexceptions.HTTPOk.code
                userquery = request.dbsession.query(UserModel)
                userquery.filter(UserModel.user_id == user_id).delete()
                request.dbsession.flush()
                result = "deleted user " + str(user_id)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )
    if request.method not in ('GET', 'PUT', 'DELETE'):
        return Response(status_code=httpexceptions.HTTPMethodNotAllowed.code)
