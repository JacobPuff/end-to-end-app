# -*- coding: utf-8 -*-
from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.views import tasklists
from server_stuffs.views import tasks
from server_stuffs.models.taskmodel import TaskModel
import json

class TaskTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_get_all_tasks(self):
        tasklist_ids = []
        task_ids = []
        # Creates all the task lists
        self.request.method = 'POST'
        self.request.body = '{"user_id": 1, "list_name": "foo1"}'
        post_response = tasklists.tasklists(self.request)
        tasklist_ids.append(json.loads(post_response.body)["d"]["list_id"])

        self.request.body = '{"user_id": 1, "list_name": "bar2"}'
        post_response = tasklists.tasklists(self.request)
        tasklist_ids.append(json.loads(post_response.body)["d"]["list_id"])


        # Creates all the tasks
        self.request.body = '{"list_id": '+ str(tasklist_ids[0]) + ', "user_id": 1, "task_name": "task foo1"}'
        post_response = tasks.tasks(self.request)
        task_ids.append(json.loads(post_response.body)["d"]["task_id"])

        self.request.body = '{"list_id": '+ str(tasklist_ids[1]) + ', "user_id": 1, "task_name": "task bar2"}'
        post_response = tasks.tasks(self.request)
        task_ids.append(json.loads(post_response.body)["d"]["task_id"])


        # Get all tasks
        self.request.method = 'GET'
        response = tasks.tasks(self.request)

        # Task 1 should correlate to list 1, and task 2 should correlate to list 2
        self.assertEqual(response.body, b'{"d": [{"task_id": ' + bytes(str(task_ids[0]), "utf-8") + b', "list_id": ' +
                         bytes(str(tasklist_ids[0]), "utf-8") + b', "user_id": 1, "task_name": "task foo1"}, ' +
                         b'{"task_id": ' + bytes(str(task_ids[1]), "utf-8") + b', "list_id": ' +
                         bytes(str(tasklist_ids[1]), "utf-8") + b', "user_id": 1, "task_name": "task bar2"}]}')

    def test_post_task(self):
        self.request.method = 'POST'
        # Create task list to pin task to
        self.request.body = '{"user_id": 1, "list_name": "list"}'
        response = tasklists.tasklists(self.request)
        list_id = json.loads(response.body)["d"]["list_id"]

        # Create one task
        self.request.body = '{"list_id": ' + str(list_id) + ', "user_id": 1, "task_name": "task"}'
        response = tasks.tasks(self.request)
        task_id = json.loads(response.body)["d"]["task_id"]
        self.assertEqual(response.body, b'{"d": {"task_id": ' + bytes(str(task_id), 'utf-8') + b', "list_id": ' +
                         bytes(str(list_id), 'utf-8') + b', "user_id": 1, "task_name": "task"}}')

    def test_get_task_by_id(self):
        self.request.method = 'POST'
        # Create task list to pin task to
        self.request.body = '{"user_id": 1, "list_name": "list"}'
        post_response = tasklists.tasklists(self.request)
        list_id = json.loads(post_response.body)["d"]["list_id"]

        # Create one task
        self.request.body = '{"list_id": ' + str(list_id) + ', "user_id": 1, "task_name": "task"}'
        post_response = tasks.tasks(self.request)
        task_id = json.loads(post_response.body)["d"]["task_id"]

        # Get task by id
        self.request.method = 'GET'
        self.request.matchdict = {"task_id": task_id}
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.body, b'{"d": {"task_id": ' + bytes(str(task_id), 'utf-8') + b', "list_id": ' +
                         bytes(str(list_id), 'utf-8') + b', "user_id": 1, "task_name": "task"}}')

    def test_put_task_by_id(self):
        self.request.method = 'POST'
        # Create task list to pin task to
        self.request.body = '{"user_id": 1, "list_name": "list"}'
        post_response = tasklists.tasklists(self.request)
        list_id = json.loads(post_response.body)["d"]["list_id"]

        # Create one task
        self.request.body = '{"list_id": ' + str(list_id) + ', "user_id": 1, "task_name": "task"}'
        post_response = tasks.tasks(self.request)
        task_id = json.loads(post_response.body)["d"]["task_id"]

        # Update the task
        self.request.method = 'PUT'
        self.request.body = '{"list_id": ' + str(list_id) + ', "user_id": 1, "task_name": "task updated"}'
        self.request.matchdict = {"task_id": task_id}
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.body, b'task ' + bytes(str(task_id), 'utf-8') + b' updated')

    def test_delete_task_by_id(self):
        self.request.method = 'POST'
        # Create task list to pin task to
        self.request.body = '{"user_id": 1, "list_name": "list"}'
        post_response = tasklists.tasklists(self.request)
        list_id = json.loads(post_response.body)["d"]["list_id"]

        # Create one task
        self.request.body = '{"list_id": ' + str(list_id) + ', "user_id": 1, "task_name": "task"}'
        post_response = tasks.tasks(self.request)
        task_id = json.loads(post_response.body)["d"]["list_id"]

        # Delete the task
        self.request.method = 'DELETE'
        self.request.matchdict = {"task_id": task_id}
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.body, b'task ' + bytes(str(task_id), 'utf-8') + b' deleted')

    def test_delete_tasklist_with_tasks(self):
        self.request.method = 'POST'
        # Create task list to pin tasks to
        self.request.body = '{"user_id": 1, "list_name": "list"}'
        post_response = tasklists.tasklists(self.request)
        list_id = json.loads(post_response.body)["d"]["list_id"]

        # Create tasks to pin
        task_ids = []
        self.request.body = '{"list_id": ' + str(list_id) + ', "user_id": 1, "task_name": "task1"}'
        post_response = tasks.tasks(self.request)
        task_ids.append(json.loads(post_response.body)["d"]["task_id"])

        self.request.body = '{"list_id": ' + str(list_id) + ', "user_id": 1, "task_name": "task2"}'
        post_response = tasks.tasks(self.request)
        task_ids.append(json.loads(post_response.body)["d"]["task_id"])

        # Delete task list
        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.body, b'task list ' + bytes(str(list_id), 'utf-8') + b' deleted')
        query = self.dbsession.query(TaskModel)
        checkEmptyList = query.filter(TaskModel.list_id == list_id).all()
        self.assertEqual(checkEmptyList, [])

    def test_get_tasks_with_tasklist_id(self):
        list_ids = []
        task_ids = []
        self.request.method = 'POST'
        # Create task lists to pin tasks to
        self.request.body = '{"user_id": 1, "list_name": "list1"}'
        post_response = tasklists.tasklists(self.request)
        list_ids.append(json.loads(post_response.body)["d"]["list_id"])

        self.request.body = '{"user_id": 1, "list_name": "list2"}'
        post_response = tasklists.tasklists(self.request)
        list_ids.append(json.loads(post_response.body)["d"]["list_id"])

        # Create tasks to pin
        self.request.body = '{"list_id": ' + str(list_ids[0]) + ', "user_id": 1, "task_name": "task1 for list_ids[0]"}'
        post_response = tasks.tasks(self.request)
        task_ids.append(json.loads(post_response.body)["d"]["task_id"])

        self.request.body = '{"list_id": ' + str(list_ids[0]) + ', "user_id": 1, "task_name": "task2 for list_ids[0]"}'
        post_response = tasks.tasks(self.request)
        task_ids.append(json.loads(post_response.body)["d"]["task_id"])

        self.request.body = '{"list_id": ' + str(list_ids[1]) + ', "user_id": 1, "task_name": "task3 for list_ids[1]"}'
        post_response = tasks.tasks(self.request)
        task_ids.append(json.loads(post_response.body)["d"]["task_id"])

        # Get tasks by list id
        self.request.method = 'GET'
        self.request.params["tasklist_id"] = str(list_ids[0])
        response = tasks.tasks(self.request)
        self.assertEqual(response.body, b'{"d": [{"task_id": ' + bytes(str(task_ids[0]), 'utf-8') + b', "list_id": ' +
                         bytes(str(list_ids[0]), 'utf-8') + b', "user_id": 1, "task_name": "task1 for list_ids[0]"}, ' +
                         b'{"task_id": ' + bytes(str(task_ids[1]), 'utf-8') + b', "list_id": ' +
                         bytes(str(list_ids[0]), 'utf-8') + b', "user_id": 1, "task_name": "task2 for list_ids[0]"}]}')

        self.request.params["tasklist_id"] = str(list_ids[1])
        response = tasks.tasks(self.request)
        self.assertEqual(response.body, b'{"d": [{"task_id": ' + bytes(str(task_ids[2]), 'utf-8') + b', "list_id": ' +
                         bytes(str(list_ids[1]), 'utf-8') + b', "user_id": 1, "task_name": "task3 for list_ids[1]"}]}')
