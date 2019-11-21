from pyramid.response import Response
from pyramid.view import view_config
from pyramid import httpexceptions
from datetime import datetime, timedelta
from uuid import uuid4
import json

from ..models import UserModel, SessionModel, ResetTokenModel, VerifyTokenModel
from ..scripts.password_hashing import pwd_context
from ..scripts.converters import dict_from_row
from ..scripts.utilities import error_dict, datetime_serializer, send_verification_email

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

def email_in_use(user_email, dbsession):
    """
    Returns true if a email exists
    :param username: a string username
    :param dbsession: a db session
    :return: True if an email exists that is verified, otherwise False
    """
    exists = dbsession.query(UserModel).filter(UserModel.user_email == user_email.lower())\
        .filter(UserModel.verified == True).one_or_none()
    return exists is not None


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
        elif email_in_use(body.get('user_email'), request.dbsession):
            status_code = httpexceptions.HTTPConflict.code
            result = error_dict("api_error", "email already in use")
        elif len(body.get("user_pass")) < 8:
            status_code = httpexceptions.HTTPBadRequest.code
            result = error_dict("api_error", "password must be at least 8 characters")
        else:
            existingUser = request.dbsession.query(UserModel)\
                .filter(UserModel.user_email == body.get("user_email").lower())\
                .filter(UserModel.verified == False).one_or_none()
            
            user = UserModel()
            if existingUser is not None:
                user = existingUser
            
            user.user_name = body["user_name"].lower()
            user.user_email = body["user_email"].lower()
            user.user_pass = pwd_context.hash(body["user_pass"])

            if existingUser is None:
                request.dbsession.add(user)
            # We use flush here so that user has a user_id because we need it for testing
            # Autocommit is true, but just in case that is turned off, we use refresh, so it pulls the user_id
            request.dbsession.flush()
            request.dbsession.refresh(user)

            # Make session
            new_token = str(uuid4())

            s = SessionModel()
            s.user_id = user.user_id
            s.token = new_token
            request.dbsession.add(s)
            request.dbsession.flush()
            request.dbsession.refresh(s)

            # Make verification token
            new_token = str(uuid4())
            verifytoken = VerifyTokenModel()
            verifytoken.user_id = user.user_id
            verifytoken.token = new_token
            request.dbsession.add(verifytoken)
            request.dbsession.flush()
            request.dbsession.refresh(verifytoken)

            error = send_verification_email(request, user.user_email, verifytoken)
            if error:
                status_code = httpexceptions.HTTPBadRequest.code
                result = error
            else:
                status_code = httpexceptions.HTTPOk.code
                result = dict_from_row(user, remove_fields=removals)
                result["session"] = dict_from_row(s)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method != 'POST':
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
                elif body.get("user_pass") and body.get("old_pass") is None:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error_dict("api_error", "old_pass required when updating password")
                elif body.get("old_pass") and body.get("user_pass") is None:
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error_dict("api_error", "user_pass required when using old_pass")
                elif body.get("old_pass") and not pwd_context.verify(body.get("old_pass"), request.user.user_pass):
                    status_code = httpexceptions.HTTPBadRequest.code
                    result = error_dict("api_error", "old_pass didnt match")
                else:
                    if body.get("user_name"):
                        request.user.user_name = body.get("user_name").lower()
                    if body.get("user_email"):
                        request.user.verified = False
                        # Check
                        # request.user.user_email = body.get("user_email").lower()
                        # Make verification token
                        new_token = str(uuid4())
                        verifytoken = VerifyTokenModel()
                        verifytoken.user_id = request.user.user_id
                        verifytoken.token = new_token
                        request.dbsession.add(verifytoken)
                        request.dbsession.flush()
                        request.dbsession.refresh(verifytoken)

                        error = send_verification_email(request, body.get("user_email").lower(), verifytoken)
                        if error:
                            status_code = httpexceptions.HTTPBadRequest.code
                            result = error
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
