from pyramid.config import Configurator
import datetime
from .models import UserModel, SessionModel

def user(request):
    """
    This function checks if the request is authenticated based on the token they provide.
    """
    request_token = 'invalid_token'
    if request.method == 'GET':
        if request.GET.get('token') is None:
            return None
        else:
            request_token = request.GET.get('token')
    elif request.method in ('PUT', 'POST', 'DELETE'):
        if 'token' not in request.json_body:
            return None
        else:
            request_token = request.json_body.get('token')

    user = request.dbsession.query(UserModel)\
        .filter(SessionModel.token == request_token)\
        .filter(SessionModel.last_active >= (datetime.datetime.utcnow() - datetime.timedelta(weeks=1)))\
        .filter(UserModel.verified == "t")\
        .join(SessionModel, SessionModel.user_id == UserModel.user_id)\
        .one_or_none()

    if user:
        session = request.dbsession.query(SessionModel).filter(SessionModel.token == request_token).one()
        session.last_active = datetime.datetime.utcnow()
        # Autocommit! Even if it wasn't on, the transaction manager calls commit after the request is done.
        request.dbsession.flush()
    return user



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('.models')
    config.include('.routes')

    config.add_request_method(callable=user,
                              name=None,
                              property=True,
                              reify=True
                              )

    config.scan()
    return config.make_wsgi_app()
