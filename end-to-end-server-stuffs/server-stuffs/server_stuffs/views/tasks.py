from pyramid.response import Response
from pyramid.view import view_config
from pyramid import httpexceptions
import json

from ..models import TaskListModel, TaskModel
from ..scripts.converters import array_of_dicts_from_array_of_models, dict_from_row
from ..scripts.utilities import error_dict


# This handles requests that don't require an id
@view_config(route_name='tasks')
def tasks(request):
    if request.method == 'GET':
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.status_code
            result = error_dict("api_error", "not authenticated for this request")
        elif request.GET.get("list_id") is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "list_id is required")
        else:
            tasklist = request.dbsession.query(TaskListModel)\
                .filter(TaskListModel.list_id == request.GET.get("list_id")).one_or_none()
            if tasklist is None:
                status_code = httpexceptions.HTTPNotFound.status_code
                result = error_dict("api_error", "list doesnt exist")
            elif tasklist.user_id != request.user.user_id:
                status_code = httpexceptions.HTTPUnauthorized.status_code
                result = error_dict("api_error", "not authenticated for this request")
            else:
                tasksforlist = request.dbsession.query(TaskModel)\
                    .filter(TaskModel.list_id == request.GET.get("list_id")).all()
                status_code = httpexceptions.HTTPOk.status_code
                result = array_of_dicts_from_array_of_models(tasksforlist)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )
    elif request.method == 'POST':
        body = request.json_body
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.status_code
            result = error_dict("api_error", "not authenticated for this request")
        elif body.get("list_id") is None or body.get("task_name") is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "list_id and task_name are required")
        else:
            tasklist = request.dbsession.query(TaskListModel)\
                .filter(TaskListModel.list_id == body.get("list_id")).one_or_none()
            if tasklist is None:
                status_code = httpexceptions.HTTPNotFound.status_code
                result = error_dict("api_error", "list doesnt exist")
            elif tasklist.user_id != request.user.user_id:
                status_code = httpexceptions.HTTPUnauthorized.status_code
                result = error_dict("api_error", "not authenticated for this request")
            else:
                task = TaskModel()
                task.list_id = body.get("list_id")
                task.task_name = body.get("task_name")
                task.user_id = request.user.user_id
                request.dbsession.add(task)
                # We use flush here so that task has a task_id because we need it for testing
                # Autocommit is true, but just in case that is turned off, we use refresh, so it pulls the task_id
                request.dbsession.flush()
                request.dbsession.refresh(task)
                status_code = httpexceptions.HTTPOk.status_code
                result = dict_from_row(task)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )

    if request.method not in ('GET', 'POST'):
        return Response(status_code=httpexceptions.HTTPMethodNotAllowed)


# This handles requests dealing with a task id
@view_config(route_name='tasks_by_id')
def tasks_by_id(request):
    task_id = request.matchdict.get('task_id')
    if request.method == 'GET':
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.status_code
            result = error_dict("api_error", "not authenticated for this request")
        elif task_id is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "task_id is required")
        else:
            task = request.dbsession.query(TaskModel)\
                .filter(TaskModel.task_id == task_id).one_or_none()
            if task is None:
                status_code = httpexceptions.HTTPNotFound.status_code
                result = error_dict("api_error", "task doesnt exist")
            else:
                tasklist = request.dbsession.query(TaskListModel)\
                    .filter(TaskListModel.list_id == task.list_id).one_or_none()
                if tasklist.user_id != request.user.user_id:
                    status_code = httpexceptions.HTTPUnauthorized.status_code
                    result = error_dict("api_error", "not authenticated for this request")
                else:
                    status_code = httpexceptions.HTTPOk.status_code
                    result = dict_from_row(task)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )
    elif request.method == 'PUT':
        body = request.json_body
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.status_code
            result = error_dict("api_error", "not authenticated for this request")
        elif task_id is None or (body.get("task_name") is None and body.get("list_id") is None and body.get("task_done") is None):
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "task_name, list_id, or task_done, and task_id are required")
        elif body.get("task_done") and isinstance(body.get("task_done"), bool) is not True:
                status_code = httpexceptions.HTTPBadRequest.status_code
                result = error_dict("api_error", "task_done must be a boolean")
        else:
            task = request.dbsession.query(TaskModel)\
                .filter(TaskModel.task_id == task_id).one_or_none()
            if task is None:
                status_code = httpexceptions.HTTPNotFound.status_code
                result = error_dict("api_error", "task doesnt exist")
            else:
                tasklist = request.dbsession.query(TaskListModel)\
                    .filter(TaskListModel.list_id == task.list_id).one_or_none()
                if tasklist.user_id != request.user.user_id:
                    status_code = httpexceptions.HTTPUnauthorized.status_code
                    result = error_dict("api_error", "not authenticated for this request")
                else:
                    if body.get("task_name"):
                        task.task_name = body.get("task_name")
                    if body.get("list_id"):
                        task.list_id = body.get("list_id")
                    if body.get("task_done"):
                        task.task_done = body.get("task_done")
                    request.dbsession.flush()
                    request.dbsession.refresh(task)
                    status_code = httpexceptions.HTTPOk.status_code
                    result = dict_from_row(task)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )
    elif request.method == 'DELETE':
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.status_code
            result = error_dict("api_error", "not authenticated for this request")
        elif task_id is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "task_id is required")
        else:
            task = request.dbsession.query(TaskModel)\
                .filter(TaskModel.task_id == task_id).one_or_none()
            if task is None:
                status_code = httpexceptions.HTTPNotFound.status_code
                result = error_dict("api_error", "task doesnt exist")
            else:
                tasklist = request.dbsession.query(TaskListModel)\
                    .filter(TaskListModel.list_id == task.list_id).one_or_none()
                if tasklist.user_id != request.user.user_id:
                    status_code = httpexceptions.HTTPUnauthorized.status_code
                    result = error_dict("api_error", "not authenticated for this request")
                else:
                    request.dbsession.delete(task)
                    request.dbsession.flush()
                    status_code = httpexceptions.HTTPOk.status_code
                    result = "task " + str(task_id) + " deleted"

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )

    if request.method not in ('GET', 'PUT', 'DELETE'):
        return Response(status_code=httpexceptions.HTTPMethodNotAllowed)
