# -*- coding: utf-8 -*-

""" Posts Services
"""
from cornice import Service
from forumsrv.utilities import array_of_dicts_from_array_of_models, dict_from_row
from forumsrv.models import User

# Sphinx doc stuff
users_desc = """
Service for getting lists of users
"""
user_by_id_desc = """
Service for working with a specific user
"""

users_svc = Service(name='users',
                    path='/api/users',
                    description=users_desc)
user_by_id_svc = Service(name='user_by_id',
                         path='/api/users/{user_id:\d+}',
                         description=user_by_id_desc)

@users_svc.get()
def users_get_view(request):
    query = request.dbsession.query(User).all()
    result = array_of_dicts_from_array_of_models(query, remove_fields='password')
    return {'d': result}

@user_by_id_svc.get()
def user_by_id_get_view(request):
    user_id = int(request.matchdict.get('user_id'))
    result = request.dbsession.query(User).filter(User.user_id == user_id).one_or_none()
    if result is not None:
        result = dict_from_row(result, remove_fields='password')
    return {'d': result}

