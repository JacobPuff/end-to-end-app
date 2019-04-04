# -*- coding: utf-8 -*-

""" Posts Services
"""
from cornice import Service
from forumsrv.utilities import array_of_dicts_from_array_of_models, dict_from_row, sqlobj_from_dict, error_dict
from forumsrv.models import Post

# Sphinx doc stuff
posts_desc = """
Service for getting lists of posts
"""
post_by_id_desc = """
Service for working with a specific post
"""

posts_svc = Service(name='posts',
                    path='/api/posts',
                    description=posts_desc)
post_by_id_svc = Service(name='post_by_id',
                         path='/api/posts/{post_id:\d+}',
                         description=post_by_id_desc)

@posts_svc.get()
def posts_get_view(request):
    result = array_of_dicts_from_array_of_models(request.dbsession.query(Post).all())
    return {'d': result}


@posts_svc.post()
def posts_post_view(request):
    post_dict = request.json_body
    print(post_dict)
    if 'post_id' in post_dict:
        request.response.status = 400
        return {'d': error_dict('value_errors', 'can not create new posts with existing post_id')}
    if 'subject' not in post_dict or 'body' not in post_dict or 'poster' not in post_dict:
        request.response.status = 400
        return {'d': error_dict('value_errors', 'poster, subject, and body are all required fields')}
    p = Post()
    sqlobj_from_dict(p, post_dict)
    request.dbsession.add(p)
    request.dbsession.flush()
    request.dbsession.refresh(p)
    result = dict_from_row(p)
    return {'d': result}

@post_by_id_svc.delete()
def post_by_id_delete_view(request):
    post_id = int(request.matchdict.get('post_id'))
    query = request.dbsession.query(Post).filter(Post.post_id == post_id)
    if query.count() == 0:
        request.response.status = 404;
        return {'d': error_dict('value_errors', 'Post not found')}
    children = request.dbsession.query(Post).filter(Post.parent == post_id).count()
    if children > 0:
        post = query.one()
        post.body = "{post deleted by user}"
        request.dbsession.flush()
        return {'d': dict_from_row(post)}
    else:
        query.delete()
        return {'d': None}
