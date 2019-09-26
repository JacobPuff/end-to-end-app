# -*- coding: utf-8 -*-
from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.views import tasklists
from server_stuffs import user

class TaskListTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_get_all_task_lists(self):
        list_ids = []
        # make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create all the task lists
        list_ids.append(self.make_list("foo1", user_id)["list_id"])
        list_ids.append(self.make_list("bar2", user_id)["list_id"])

        # Get all the task lists
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": [{"list_id": list_ids[0], "user_id": user_id, "list_name": "foo1"},
                                                    {"list_id": list_ids[1],"user_id": user_id, "list_name": "bar2"}]})

    def test_get_all_task_lists_no_token(self):
        # make user
        self.make_user()

        # Get all the task lists
        self.request.method = 'GET'
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_all_task_lists_no_task_lists(self):
        # make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Get all the task lists
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": []})

    def test_post_task_list(self):
        # make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        list_id = response.json_body["d"]["list_id"]
        self.assertEqual(response.json_body, {"d": {"list_id": list_id, "user_id": user_id, "list_name": "foo1"}})

    def test_post_task_list_no_token(self):
        # make user
        self.make_user()

        self.request.method = 'POST'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_post_task_list_no_list_name(self):
        # make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        self.request.method = 'POST'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_name is required"]}})

    def test_get_task_list_by_id(self):
        # make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create one list
        list_id = self.make_list("foo1", user_id)["list_id"]

        # Get one list
        self.request.method = 'GET'
        self.request.matchdict = {"list_id": list_id}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"list_id": list_id, "user_id": user_id, "list_name": "foo1"}})

    def test_get_task_list_by_id_no_token(self):
        # make user
        self.make_user()

        # Get one list
        self.request.method = 'GET'
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_task_list_by_id_no_list_id(self):
        # make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Get one list
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id is required"]}})

    def test_get_task_list_by_id_nonexistent_list(self):
        # make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create one list to get the latest list_id
        list_id = self.make_list("foo1", user_id)["list_id"]

        # Get one list
        self.request.method = 'GET'
        self.request.matchdict = {"list_id": list_id + 1}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list doesnt exist"]}})

    def test_get_task_list_by_id_different_user(self):
        # Make user one
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Create one list for user one
        list_id = self.make_list("foo1", user_id)["list_id"]

        # Make user two
        token = self.make_user("differentUser", "differentEmail@jacob.squizzlezig.com")["session"]["token"]

        # Get one list
        self.request.method = 'GET'
        self.request.matchdict = {"list_id": list_id}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_put_task_list_by_id(self):
        # make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create one list
        list_id = self.make_list("foo1", user_id)["list_id"]

        # Update list
        self.request.method = 'PUT'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"list_name": "put foo1", "token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"list_id": list_id, "user_id": user_id, "list_name": "put foo1"}})

    def test_put_task_list_by_id_no_token(self):
        # make user
        self.make_user()

        # Update list
        self.request.method = 'PUT'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_put_task_list_by_id_no_list_id(self):
        # make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Update list
        self.request.method = 'PUT'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id is required"]}})

    def test_put_task_list_by_id_different_user(self):
        # Make user one
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Create one list for user one
        list_id = self.make_list("foo1", user_id)["list_id"]

        # Make user two
        user_data = self.make_user("differentUser", "differentEmail@jacob.squizzlezig.com")
        token = user_data["session"]["token"]

        # Update list
        self.request.method = 'PUT'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"list_name": "put foo1", "token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_delete_task_list_by_id(self):
        # make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Create one list
        list_id = self.make_list("foo1", user_id)["list_id"]

        # Delete list
        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task list " + str(list_id) + " deleted"})

    def test_delete_task_list_by_id_no_token(self):
        # make user
        self.make_user()

        # Delete list
        self.request.method = 'DELETE'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_delete_task_list_by_id_no_list_id(self):
        # make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Delete list
        self.request.method = 'DELETE'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id is required"]}})

    def test_delete_task_list_by_id_different_user(self):
        # Make user one
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Create one list for user one
        list_id = self.make_list("foo1", user_id)["list_id"]

        # Make user two
        user_data = self.make_user("differentUser", "differentEmail@jacob.squizzlezig.com")
        token = user_data["session"]["token"]

        # Delete list
        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})
