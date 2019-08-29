from pyramid.response import Response
from pyramid.view import view_config
from pyramid import httpexceptions
import json

from ..models import TaskListModel
from ..scripts.utilities import error_dict
from ..scripts.converters import array_of_dicts_from_array_of_models, dict_from_row


# This handles requests that don't require an id
@view_config(route_name='tasklists')
def tasklists(request):
    if request.method == 'GET':
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.status_code
            result = error_dict("api_error", "not authenticated for this request")
        else:
            query = request.dbsession.query(TaskListModel)
            tasklists_for_user = query.filter(TaskListModel.user_id == request.user.user_id).all()
            status_code = httpexceptions.HTTPOk.status_code
            result = array_of_dicts_from_array_of_models(tasklists_for_user)

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
        elif body.get("list_name") is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "list_name is required")
        else:
            tasklist = TaskListModel()
            tasklist.list_name = body.get("list_name")
            tasklist.user_id = request.user.user_id
            request.dbsession.add(tasklist)
            # We use flush here so that tasklist has a list_id because we need it for testing
            # Autocommit is true, but just in case that is turned off, we use refresh, so it pulls the list_id
            request.dbsession.flush()
            request.dbsession.refresh(tasklist)
            status_code = httpexceptions.HTTPOk.status_code
            result = dict_from_row(tasklist)

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )

    return Response(status_code=httpexceptions.HTTPMethodNotAllowed)


# This handles requests dealing with a list id
@view_config(route_name='tasklists_by_id')
def tasklists_by_id(request):
    list_id = request.matchdict.get("list_id")
    if request.method == 'GET':
        if request.user is None:
            status_code = httpexceptions.HTTPUnauthorized.status_code
            result = error_dict("api_error", "not authenticated for this request")
        elif list_id is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "list_id is required")
        else:
            resultlist = request.dbsession.query(TaskListModel)\
                .filter(TaskListModel.list_id == list_id).one_or_none()
            if resultlist is None:
                status_code = httpexceptions.HTTPNotFound.status_code
                result = error_dict("api_error", "list doesnt exist")
            elif resultlist.user_id != request.user.user_id:
                status_code = httpexceptions.HTTPUnauthorized.status_code
                result = error_dict("api_error", "not authenticated for this request")
            else:
                status_code = httpexceptions.HTTPOk.status_code
                result = dict_from_row(resultlist)

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
        elif list_id is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "list_id is required")
        elif body.get("list_name") is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "list_name is required")
        else:
            tasklist = request.dbsession.query(TaskListModel).filter(TaskListModel.list_id == list_id).one_or_none()
            if tasklist is None:
                status_code = httpexceptions.HTTPNotFound.status_code
                result = error_dict("api_error", "list doesnt exist")
            elif tasklist.user_id != request.user.user_id:
                status_code = httpexceptions.HTTPUnauthorized.status_code
                result = error_dict("api_error", "not authenticated for this request")
            else:
                tasklist.list_name = body.get("list_name")
                request.dbsession.flush()
                request.dbsession.refresh(tasklist)
                status_code = httpexceptions.HTTPOk.status_code
                result = dict_from_row(tasklist)

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
        elif list_id is None:
            status_code = httpexceptions.HTTPBadRequest.status_code
            result = error_dict("api_error", "list_id is required")
        else:
            tasklist = request.dbsession.query(TaskListModel).filter(TaskListModel.list_id == list_id).one_or_none()
            if tasklist is None:
                status_code = httpexceptions.HTTPNotFound.status_code
                result = error_dict("api_error", "list doesnt exist")
            elif tasklist.user_id != request.user.user_id:
                status_code = httpexceptions.HTTPUnauthorized.status_code
                result = error_dict("api_error", "not authenticated for this request")
            else:
                request.dbsession.delete(tasklist)
                request.dbsession.flush()
                status_code = httpexceptions.HTTPOk.status_code
                result = "task list " + str(list_id) + " deleted"

        return Response(
            content_type='application/json',
            charset='UTF-8',
            status_code=status_code,
            body=json.dumps({"d": result})
        )

    return Response(status_code=httpexceptions.HTTPMethodNotAllowed)
