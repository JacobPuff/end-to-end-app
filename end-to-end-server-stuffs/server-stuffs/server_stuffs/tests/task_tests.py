# -*- coding: utf-8 -*-
from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.views import tasklists, tasks
from server_stuffs.models import TaskModel
from server_stuffs import user

class TaskTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_get_tasks_for_list(self):
        list_ids = []
        task_ids = []
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task lists to pin tasks to
        list_ids.append(self.make_list("list1", user_id)["list_id"])
        list_ids.append(self.make_list("list2", user_id)["list_id"])

        # Create tasks to pin
        task_ids.append(self.make_task(list_ids[0], "task1 for list_ids[0]")["task_id"])
        task_ids.append(self.make_task(list_ids[0], "task2 for list_ids[0]")["task_id"])
        task_ids.append(self.make_task(list_ids[1], "task3 for list_ids[1]")["task_id"])

        # Get tasks for list 0
        self.request.method = 'GET'
        self.request.GET = {"list_id": list_ids[0], "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": [{"task_id": task_ids[0], "list_id": list_ids[0],
                                                     "task_name": "task1 for list_ids[0]", "task_done": False},
                                                    {"task_id": task_ids[1], "list_id": list_ids[0],
                                                     "task_name": "task2 for list_ids[0]", "task_done": False}]})

        # Get tasks for list 1
        self.request.GET = {"list_id": list_ids[1], "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": [{"task_id": task_ids[2], "list_id": list_ids[1],
                                                     "task_name": "task3 for list_ids[1]", "task_done": False}]})

    def test_get_tasks_for_list_no_token(self):
        # Get tasks for list
        self.request.method = 'GET'
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_tasks_for_list_no_list_id(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Get tasks for list
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id is required"]}})

    def test_get_all_tasks_for_list_nonexistent_list(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task lists to get latest list_id
        list_id = self.make_list("list", user_id)["list_id"]

        # Get tasks for list
        self.request.method = 'GET'
        self.request.GET = {"list_id": list_id + 1, "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list doesnt exist"]}})

    def test_get_all_tasks_for_list_different_user(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        user_data = self.make_user("differentUser", "differentEmail@jacob.squizzlezig.com")
        token = user_data["session"]["token"]

        # Get all tasks
        self.request.method = 'GET'
        self.request.GET = {"token": token, "list_id": list_id}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_post_task(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one task
        self.request.method = 'POST'
        self.request.json_body = {"list_id": list_id, "task_name": "task", "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        task_id = response.json_body["d"]["task_id"]
        self.assertEqual(response.json_body, {"d": {"task_id": task_id,
                                                    "list_id": list_id,
                                                    "task_name": "task",
                                                    "task_done": False}})

    def test_post_task_with_task_done(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one task
        self.request.method = 'POST'
        self.request.json_body = {"list_id": list_id, "task_name": "task", "task_done": True, "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        task_id = response.json_body["d"]["task_id"]
        self.assertEqual(response.json_body, {"d": {"task_id": task_id,
                                                    "list_id": list_id,
                                                    "task_name": "task",
                                                    "task_done": True}})

    def test_post_task_no_token(self):
        # Create one task
        self.request.method = 'POST'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_post_task_no_list_id(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Create one task
        self.request.method = 'POST'
        self.request.json_body = {"task_name": "task", "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id and task_name are required"]}})

    def test_post_task_no_task_name(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one task
        self.request.method = 'POST'
        self.request.json_body = {"list_id": list_id, "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id and task_name are required"]}})

    def test_post_task_no_list_id_or_task_name(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        self.make_list("list", user_id)

        # Create one task
        self.request.method = 'POST'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id and task_name are required"]}})

    def test_post_task_with_task_done_not_a_boolean(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one task
        self.request.method = 'POST'
        self.request.json_body = {"list_id": list_id, "task_name": "task",
                                  "task_done": "Not a boolean", "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["task_done must be a boolean"]}})

    def test_post_task_different_user_list(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        user_data = self.make_user("differentUser", "differentEmail@jacob.squizzlezig.com")
        token = user_data["session"]["token"]

        # Create one task
        self.request.method = 'POST'
        self.request.json_body = {"list_id": list_id, "task_name": "task", "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_task_by_id(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one task
        task_id = self.make_task(list_id, "task")["task_id"]

        # Get task by id
        self.request.method = 'GET'
        self.request.matchdict = {"task_id": task_id}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"task_id": task_id,
                                                    "list_id": list_id,
                                                    "task_name": "task",
                                                    "task_done": False}})

    def test_get_task_by_id_no_token(self):
        # Get task by id
        self.request.method = 'GET'
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_task_by_id_no_task_id(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Get task by id
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["task_id is required"]}})

    def test_get_task_by_id_nonexistent_task(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one list to get the latest list_id
        task_id = self.make_task(list_id, "task")["task_id"]

        # Get task by id
        self.request.method = 'GET'
        self.request.matchdict = {"task_id": task_id + 1}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["task doesnt exist"]}})

    def test_put_task_by_id(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one task
        task_id = self.make_task(list_id, "task")["task_id"]

        # Update the task
        self.request.method = 'PUT'
        self.request.matchdict = {"task_id": task_id}
        self.request.json_body = {"list_id": list_id, "task_name": "task updated","task_done": True, "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"task_id": task_id,
                                                    "list_id": list_id,
                                                    "task_name": "task updated",
                                                    "task_done": True}})

    def test_put_task_by_id_task_done_non_bool(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one task
        task_id = self.make_task(list_id, "task")["task_id"]

        # Update the task
        self.request.method = 'PUT'
        self.request.matchdict = {"task_id": task_id}
        self.request.json_body = {"list_id": list_id, "task_name": "task updated",
                                  "task_done": "Not a boolean", "token": token}
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["task_done must be a boolean"]}})

    def test_put_task_by_id_no_task_id(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Update the task
        self.request.method = 'PUT'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["task_name, list_id, or task_done, and task_id are required"]}})

    def test_delete_task_by_id(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create one task
        task_id = self.make_task(list_id, "task")["task_id"]

        # Delete the task
        self.request.method = 'DELETE'
        self.request.matchdict = {"task_id": task_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task " + str(task_id) + " deleted"})

    def test_delete_task_by_id_no_token(self):
        # Delete the task
        self.request.method = 'DELETE'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = tasks.tasks_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_delete_tasklist_with_tasks(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create task list to pin task to
        list_id = self.make_list("list", user_id)["list_id"]

        # Create tasks
        self.make_task(list_id, "task1")
        self.make_task(list_id, "task2")

        # Delete task list
        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task list " + str(list_id) + " deleted"})
        query = self.dbsession.query(TaskModel)
        checkEmptyList = query.filter(TaskModel.list_id == list_id).all()
        self.assertEqual(checkEmptyList, [])
