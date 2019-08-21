from pyramid.response import Response
from pyramid.view import view_config
from datetime import datetime, timedelta
from uuid import uuid4
import json

from ..models import UserModel, SessionModel
from ..scripts.password_hashing import pwd_context
from ..scripts.converters import array_of_dicts_from_array_of_models, dict_from_row, sqlobj_from_dict
from ..scripts.utilities import error_dict, datetime_serializer

@view_config(route_name='sessions')
def sessions(request):
    if request.method == 'POST':
        result = {}
        status_code = 200
        body = request.json_body
        userquery = request.dbsession.query(UserModel)
        sessionquery = request.dbsession.query(SessionModel)
        if request.user is not None:
            result = dict_from_row(sessionquery.filter(SessionModel.token == request.json_body.get('token')).one())
        else:
            if not ("user_name" in body or "user_email" in body) or not "user_pass" in body:
                status_code = 400
                result = error_dict("api_error", "Username or email, and password needed")
            else:
                if body.get('user_name') is not None:
                    user = userquery.filter(UserModel.user_name == body["user_name"].lower()).first()
                elif body.get('user_email') is not None:
                    user = userquery.filter(UserModel.user_email == body["user_email"].lower()).first()

                if not user or not pwd_context.verify(body["user_pass"], user.user_pass):
                    status_code = 400
                    result = error_dict("api_error", "User doesn't exist")

        if not result:
            new_token = str(uuid4())

            new_session = SessionModel()
            new_session.user_id = user.user_id
            new_session.token = new_token
            request.dbsession.add(new_session)
            # We use flush here so that new_session has a session_id because we need it for testing
            # Autocommit is true, but just in case that is turned off, we use refresh, so it pulls the session_id
            request.dbsession.flush()
            request.dbsession.refresh(new_session)
            result = dict_from_row(new_session)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method == 'PUT':
        result = {}
        status_code = 200
        if request.user is None:
            status_code = 400
            result = error_dict("api_error", "not authenticated for this request")
        else:
            token = request.json_body.get('token')
            session = request.dbsession.query(SessionModel).filter(SessionModel.token == token,
                                                                   SessionModel.user_id == request.user.user_id).one_or_none()
            if session is None and result == {}:
                status_code = 400
                result = error_dict("api_error", "no valid token provided")
            elif result == {}:
                expiration_value = timedelta(weeks=1)
                if(datetime.utcnow() - expiration_value) > session.last_active:
                    status_code = 400
                    result = error_dict("api_error", "no valid token provided")
                elif result == {}:
                    session.last_active = datetime.utcnow()
                    request.dbsession.flush()

                    result = dict_from_row(session)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )

    if request.method == 'DELETE':
        result = {}
        status_code = 200
        if request.user is None:
            status_code = 400
            result = error_dict("api_error", "not authenticated for this request")
        token = request.json_body.get('token')
        if token is None and result == {}:
            status_code = 400
            result = error_dict("api_error", "no valid token provided")
        elif result == {}:
            session = request.dbsession.query(SessionModel).filter(SessionModel.token == token).one_or_none()
            if session is None:
                status_code = 400
                result = error_dict("api_error", "no valid token provided")
            elif result == {}:
                request.dbsession.query(SessionModel).filter(SessionModel.session_id == session.session_id).delete()
                result = "deleted session"
        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )
