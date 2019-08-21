from pyramid.response import Response
from pyramid.view import view_config
from uuid import uuid4
import json

from ..models import UserModel, SessionModel
from ..scripts.password_hashing import pwd_context
from ..scripts.converters import array_of_dicts_from_array_of_models, dict_from_row, sqlobj_from_dict
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
        status_code = 200
        body = request.json_body

        if username_in_use(body["user_name"], request.dbsession):
            status_code = 400
            result = error_dict("api_error", "Username already in use")
        else:
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
        return "password reset request. The update should happen on the users/id url"


# This handles requests without a user_id
@view_config(route_name='users_by_id')
def users_by_id(request):
    user_id = request.match['user_id']
    if request.method == 'GET':
        result = {}
        status_code = 200
        body = request.json_body

        if request.user is None:
            status_code = 400
            result = error_dict("api_errors", "not authenticated for this request")
        else:
            return
        return

    if request.method == 'DELETE':
        return "Delete user"
