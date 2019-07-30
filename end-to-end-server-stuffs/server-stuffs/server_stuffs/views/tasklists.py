from pyramid.response import Response
from pyramid.view import view_config
import json

from ..models import TaskListModel
from ..scripts.converters import array_of_dicts_from_array_of_models, dict_from_row, sqlobj_from_dict


# This handles requests that don't require an id
@view_config(route_name='tasklists')
def tasklists(request):
    if request.method == 'GET':
        query = request.dbsession.query(TaskListModel)
        tasklists = query.all()
        result = array_of_dicts_from_array_of_models(tasklists)
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body=json.dumps({'d': result})
        )
    elif request.method == 'POST':
        body = json.loads(request.body)
        tasklist = sqlobj_from_dict(TaskListModel(), body)
        request.dbsession.add(tasklist)
        # We use flush here so that tasklist has a list_id because we need it for testing
        request.dbsession.flush()
        result = dict_from_row(tasklist)
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body=json.dumps({'d': result})
        )


# This handles requests dealing with a list id
@view_config(route_name='tasklists_by_id')
def tasklists_by_id(request):
    list_id = request.matchdict['list_id']
    if request.method == 'GET':
        query = request.dbsession.query(TaskListModel)
        tasklist = query.filter(TaskListModel.list_id == list_id).first()
        result = dict_from_row(tasklist)
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body=json.dumps({'d': result})
        )
    elif request.method == 'PUT':
        body = json.loads(request.body)
        query = request.dbsession.query(TaskListModel)
        query.filter(TaskListModel.list_id == list_id).\
            update({TaskListModel.list_name: body['list_name']})
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body="task list " + str(list_id) + " updated"
        )
    elif request.method == 'DELETE':
        query = request.dbsession.query(TaskListModel)
        query.filter(TaskListModel.list_id == list_id).delete()
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body="task list " + str(list_id) + " deleted"
        )
