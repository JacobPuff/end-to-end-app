# -*- coding: utf-8 -*-
from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.views import tasklists, tasks, users
from server_stuffs.models.taskmodel import TaskModel
from server_stuffs import user


def make_user(self):
    self.request.method = 'POST'
    self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
    response = users.users(self.request)
    return response.json_body["d"]


class TaskTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_get_all_tasks(self):
        tasklist_ids = []
        task_ids = []
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        # Creates all the task lists
        self.request.method = 'POST'
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "foo1"}
        post_response = tasklists.tasklists(self.request)
        tasklist_ids.append(post_response.json_body["d"]["list_id"])

        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "bar2"}
        post_response = tasklists.tasklists(self.request)
        tasklist_ids.append(post_response.json_body["d"]["list_id"])


        # Creates all the tasks
        self.request.json_body = {"list_id": tasklist_ids[0], "task_name": "task foo1"}
        post_response = tasks.tasks(self.request)
        task_ids.append(post_response.json_body["d"]["task_id"])

        self.request.json_body = {"list_id": tasklist_ids[1], "task_name": "task bar2"}
        post_response = tasks.tasks(self.request)
        task_ids.append(post_response.json_body["d"]["task_id"])


        # Get all tasks
        self.request.method = 'GET'
        response = tasks.tasks(self.request)

        # Task 1 should correlate to list 1, and task 2 should correlate to list 2
        self.assertEqual(response.json_body, {"d": [{"task_id": task_ids[0], "list_id": tasklist_ids[0],
                                                "task_name": "task foo1"}, {"task_id": task_ids[1],
                                                "list_id": tasklist_ids[1], "task_name": "task bar2"}]})

    def test_post_task(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        # Create task list to pin task to
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "list"}
        response = tasklists.tasklists(self.request)
        list_id = response.json_body["d"]["list_id"]

        # Create one task
        self.request.json_body = {"list_id": list_id, "task_name": "task"}
        response = tasks.tasks(self.request)
        task_id = response.json_body["d"]["task_id"]
        self.assertEqual(response.json_body, {"d": {"task_id": task_id, "list_id": list_id, "task_name": "task"}})

    def test_get_task_by_id(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        # Create task list to pin task to
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "list"}
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Create one task
        self.request.json_body = {"list_id": list_id, "task_name": "task"}
        post_response = tasks.tasks(self.request)
        task_id = post_response.json_body["d"]["task_id"]

        # Get task by id
        self.request.method = 'GET'
        self.request.matchdict = {"task_id": str(task_id)}
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"task_id": task_id, "list_id": list_id, "task_name": "task"}})

    def test_put_task_by_id(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        # Create task list to pin task to
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "list"}
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Create one task
        self.request.json_body = {"list_id": list_id, "task_name": "task"}
        post_response = tasks.tasks(self.request)
        task_id = post_response.json_body["d"]["task_id"]

        # Update the task
        self.request.method = 'PUT'
        self.request.json_body = {"list_id": list_id, "task_name": "task updated"}
        self.request.matchdict = {"task_id": str(task_id)}
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task " + str(task_id) + " updated"})

    def test_delete_task_by_id(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        # Create task list to pin task to
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "list"}
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Create one task
        self.request.json_body = {"list_id": list_id, "task_name": "task"}
        post_response = tasks.tasks(self.request)
        task_id = post_response.json_body["d"]["list_id"]

        # Delete the task
        self.request.method = 'DELETE'
        self.request.matchdict = {"task_id": str(task_id)}
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task " + str(task_id) + " deleted"})

    def test_delete_tasklist_with_tasks(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        # Create task list to pin tasks to
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "list"}
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Create tasks to pin
        task_ids = []
        self.request.json_body = {"list_id": list_id, "task_name": "task1"}
        post_response = tasks.tasks(self.request)
        task_ids.append(post_response.json_body["d"]["task_id"])

        self.request.json_body = {"list_id": list_id, "task_name": "task2"}
        post_response = tasks.tasks(self.request)
        task_ids.append(post_response.json_body["d"]["task_id"])

        # Delete task list
        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task list " + str(list_id) + " deleted"})
        query = self.dbsession.query(TaskModel)
        checkEmptyList = query.filter(TaskModel.list_id == list_id).all()
        self.assertEqual(checkEmptyList, [])

    def test_get_tasks_with_tasklist_id(self):
        list_ids = []
        task_ids = []
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        # Create task lists to pin tasks to
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "list1"}
        post_response = tasklists.tasklists(self.request)
        list_ids.append(post_response.json_body["d"]["list_id"])

        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "list2"}
        post_response = tasklists.tasklists(self.request)
        list_ids.append(post_response.json_body["d"]["list_id"])

        # Create tasks to pin
        self.request.json_body = {"list_id": list_ids[0], "task_name": "task1 for list_ids[0]"}
        post_response = tasks.tasks(self.request)
        task_ids.append(post_response.json_body["d"]["task_id"])

        self.request.json_body = {"list_id": list_ids[0], "task_name": "task2 for list_ids[0]"}
        post_response = tasks.tasks(self.request)
        task_ids.append(post_response.json_body["d"]["task_id"])

        self.request.json_body = {"list_id": list_ids[1], "task_name": "task3 for list_ids[1]"}
        post_response = tasks.tasks(self.request)
        task_ids.append(post_response.json_body["d"]["task_id"])

        # Get tasks by list id
        self.request.method = 'GET'
        self.request.params["tasklist_id"] = str(list_ids[0])
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": [{"task_id": task_ids[0], "list_id": list_ids[0],
                                                     "task_name": "task1 for list_ids[0]"},
                                                    {"task_id": task_ids[1], "list_id": list_ids[0],
                                                     "task_name": "task2 for list_ids[0]"}]})

        self.request.params["tasklist_id"] = str(list_ids[1])
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": [{"task_id": task_ids[2], "list_id": list_ids[1],
                                                     "task_name": "task3 for list_ids[1]"}]})
