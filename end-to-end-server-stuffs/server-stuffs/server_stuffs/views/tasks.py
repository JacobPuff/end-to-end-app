from pyramid.response import Response
from pyramid.view import view_config
import json

from ..models import TaskModel
from ..scripts.converters import array_of_dicts_from_array_of_models, dict_from_row, sqlobj_from_dict


# This handles requests that don't require an id
@view_config(route_name='tasks')
def tasks(request):
    if request.method == 'GET' and (not 'tasklist_id' in request.params or not request.params['tasklist_id'].isdigit()):
        query = request.dbsession.query(TaskModel)
        tasks = query.all()
        result = array_of_dicts_from_array_of_models(tasks)
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body=json.dumps({'d': result})
        )
    elif request.method == 'GET' and 'tasklist_id' in request.params and request.params['tasklist_id'].isdigit():
        query = request.dbsession.query(TaskModel)
        tasksforlist = query.filter(TaskModel.list_id == int(request.params['tasklist_id'])).all()
        result = array_of_dicts_from_array_of_models(tasksforlist)
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body=json.dumps({'d': result})
        )
    elif request.method == 'POST':
        body = json.loads(request.body)
        task = sqlobj_from_dict(TaskModel(), body)
        request.dbsession.add(task)
        # We use flush here so that task has a task_id because we need it for testing
        request.dbsession.flush()
        result = dict_from_row(task)
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body=json.dumps({'d': result})
        )


# This handles requests dealing with a task id
@view_config(route_name='tasks_by_id')
def tasks_by_id(request):
    task_id = request.matchdict['task_id']
    if request.method == 'GET':
        query = request.dbsession.query(TaskModel)
        task = query.filter(TaskModel.task_id == task_id).first()
        result = dict_from_row(task)
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body=json.dumps({'d': result})
        )
    elif request.method == 'PUT':
        body = json.loads(request.body)
        query = request.dbsession.query(TaskModel)
        query.filter(TaskModel.task_id == task_id).\
            update({TaskModel.task_name: body['task_name']})
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body="task " + str(task_id) + " updated"
        )
    elif request.method == 'DELETE':
        query = request.dbsession.query(TaskModel)
        query.filter(TaskModel.task_id == task_id).delete()
        return Response(
            content_type='application/json',
            charset='UTF-8',
            body="task " + str(task_id) + " deleted"
        )
