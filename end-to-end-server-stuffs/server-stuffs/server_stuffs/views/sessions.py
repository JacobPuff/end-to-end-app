from pyramid.response import Response
from pyramid.view import view_config
from datetime import datetime, timedelta
from uuid import uuid4
import json

from ..models import UserModel, SessionModel
from ..scripts.password_hashing import pwd_context
from ..scripts.converters import dict_from_row
from ..scripts.utilities import error_dict, datetime_serializer

@view_config(route_name='sessions')
def sessions(request):
    if request.method == 'POST':
        body = request.json_body
        userquery = request.dbsession.query(UserModel)
        sessionquery = request.dbsession.query(SessionModel)

        if request.user is not None:
            status_code = 200
            result = dict_from_row(sessionquery.filter(SessionModel.token == request.json_body.get('token')).one())
        else:
            if not ("user_name" in body or "user_email" in body) or "user_pass" not in body:
                status_code = 400
                result = error_dict("api_error", "username or email, and password are required")
            else:
                if body.get('user_name') is not None:
                    user = userquery.filter(UserModel.user_name == body["user_name"].lower()).one_or_none()
                elif body.get('user_email') is not None:
                    user = userquery.filter(UserModel.user_email == body["user_email"].lower()).one_or_none()

                if user is None or not pwd_context.verify(body["user_pass"], user.user_pass):
                    status_code = 400
                    result = error_dict("api_error", "user doesn't exist")

                else:
                    status_code = 200
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
        if request.user is None:
            status_code = 400
            result = error_dict("api_error", "not authenticated for this request")
        else:
            sessionquery = request.dbsession.query(SessionModel)
            sessionquery.filter(SessionModel.last_active < (datetime.now() - timedelta(weeks=1))).delete()

            token = request.json_body.get('token')
            session = sessionquery.filter(SessionModel.token == token).one_or_none()
            session.last_active = datetime.utcnow()
            request.dbsession.flush()
            status_code = 200
            result = dict_from_row(session)

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
            token = request.json_body.get('token')
            request.dbsession.query(SessionModel).filter(SessionModel.token == token)\
                .filter(SessionModel.user_id == request.user.user_id).delete()
            request.dbsession.flush()
            status_code = 200
            result = "deleted session"

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result}, default=datetime_serializer)
        )
