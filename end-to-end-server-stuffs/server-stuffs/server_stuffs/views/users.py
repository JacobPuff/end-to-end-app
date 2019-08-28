from pyramid.response import Response
from pyramid.view import view_config
from uuid import uuid4
import json

from ..models import UserModel, SessionModel
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


# This handles requests without a user_id
@view_config(route_name='users')
def users(request):
    if request.method == 'POST':
        body = request.json_body

        if "user_name" not in body or "user_email" not in body or "user_pass" not in body:
            status_code = 400
            result = error_dict("api_error", "username, email, and password are required")
        elif username_in_use(body.get('user_name'), request.dbsession):
            status_code = 400
            result = error_dict("api_error", "username already in use")
        elif len(body.get("user_pass")) < 8:
            status_code = 400
            result = error_dict("api_error", "password must be at least 8 characters")
        else:
            status_code = 200
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
        # password reset request. The update should happen on the users/id url
        # A delay happened, so I'm going to work on something else while I wait.
        return Response(body="Not implemented yet")


# This handles requests with a user_id
@view_config(route_name='users_by_id')
def users_by_id(request):
    user_id = request.matchdict.get('user_id')
    if request.method == 'GET':
        if request.user is None:
            status_code = 400
            result = error_dict("api_error", "not authenticated for this request")
        else:
            if user_id is None or int(user_id) != request.user.user_id:
                status_code = 400
                result = error_dict("api_error", "not authenticated for this request")
            else:
                status_code = 200
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
            status_code = 400
            result = error_dict("api_error", "not authenticated for this request")
        else:
            if user_id is None or int(user_id) != request.user.user_id:
                status_code = 400
                result = error_dict("api_error", "not authenticated for this request")
            elif body.get("user_name") is None and body.get("user_email") is None and body.get("user_pass") is None:
                status_code = 400
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
                status_code = 200
                result = dict_from_row(request.user, remove_fields=removals)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method == 'DELETE':
        if request.user is None:
            status_code = 400
            result = error_dict("api_error", "not authenticated for this request")
        else:
            if user_id is None or int(user_id) != request.user.user_id:
                status_code = 400
                result = error_dict("api_error", "not authenticated for this request")
            else:
                status_code = 200
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
