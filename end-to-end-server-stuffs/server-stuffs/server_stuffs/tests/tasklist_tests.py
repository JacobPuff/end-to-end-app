# -*- coding: utf-8 -*-
from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.views import tasklists, users
from server_stuffs import user

def make_user(self):
    self.request.method = 'POST'
    self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
    response = users.users(self.request)
    return response.json_body["d"]


class TaskListTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_get_all_task_lists(self):
        list_ids = []
        # make user
        user_response = make_user(self)
        user_id = user_response["user_id"]
        token = user_response["session"]["token"]

        # Create all the task lists
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_ids.append(post_response.json_body["d"]["list_id"])

        self.request.json_body = {"list_name": "bar2", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_ids.append(post_response.json_body["d"]["list_id"])

        # Get all the task lists
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": [{"list_id": list_ids[0], "user_id": user_id, "list_name": "foo1"},
                                               {"list_id": list_ids[1],"user_id": user_id, "list_name": "bar2"}]})

    def test_get_all_task_lists_no_token(self):
        list_ids = []
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Create all the task lists
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_ids.append(post_response.json_body["d"]["list_id"])

        self.request.json_body = {"list_name": "bar2", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_ids.append(post_response.json_body["d"]["list_id"])

        # Get all the task lists
        self.request.method = 'GET'
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_all_task_lists_no_task_lists(self):
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Get all the task lists
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": []})

    def test_post_task_list(self):
        # make user
        user_response = make_user(self)
        user_id = user_response["user_id"]
        token = user_response["session"]["token"]

        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        list_id = response.json_body["d"]["list_id"]
        self.assertEqual(response.json_body, {"d": {"list_id": list_id, "user_id": user_id, "list_name": "foo1"}})

    def test_post_task_list_no_token(self):
        # make user
        make_user(self)

        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1"}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_post_task_list_no_list_name(self):
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        self.request.method = 'POST'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_name is required"]}})

    def test_get_task_list_by_id(self):
        # make user
        user_response = make_user(self)
        user_id = user_response["user_id"]
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Get one list
        self.request.method = 'GET'
        self.request.matchdict = {"list_id": list_id}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"list_id": list_id, "user_id": user_id, "list_name": "foo1"}})

    def test_get_task_list_by_id_no_token(self):
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Get one list
        self.request.method = 'GET'
        self.request.matchdict = {"list_id": list_id}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_task_list_by_id_no_list_id(self):
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        tasklists.tasklists(self.request)

        # Get one list
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id is required"]}})

    def test_get_task_list_by_id_nonexistent_list(self):
        # make user
        user_response = make_user(self)
        user_id = user_response["user_id"]
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

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
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com",
                                  "user_pass": "TestPass"}
        user_response = users.users(self.request).json_body["d"]
        token = user_response["session"]["token"]

        # Create one list for user one
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request).json_body["d"]
        list_id = post_response["list_id"]

        # Make user two
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "DifferentUser", "user_email": "test@squizzlezig.com",
                                  "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        token = post_response["session"]["token"]

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
        user_response = make_user(self)
        user_id = user_response["user_id"]
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Update list
        self.request.method = 'PUT'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"list_name": "put foo1", "token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"list_id": list_id, "user_id": user_id, "list_name": "put foo1"}})

    def test_put_task_list_by_id_no_token(self):
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Update list
        self.request.method = 'PUT'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"list_name": "put foo1"}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_put_task_list_by_id_no_list_id(self):
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        tasklists.tasklists(self.request)

        # Update list
        self.request.method = 'PUT'
        self.request.json_body = {"list_name": "put foo1", "token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id is required"]}})

    def test_put_task_list_by_id_different_user(self):
        # Make user one
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com",
                                  "user_pass": "TestPass"}
        user_response = users.users(self.request).json_body["d"]
        token = user_response["session"]["token"]

        # Create one list for user one
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request).json_body["d"]
        list_id = post_response["list_id"]

        # Make user two
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "DifferentUser", "user_email": "test@squizzlezig.com",
                                  "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        token = post_response["session"]["token"]

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
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Delete list
        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task list " + str(list_id) + " deleted"})

    def test_delete_task_list_by_id_no_token(self):
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Delete list
        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_delete_task_list_by_id_no_list_id(self):
        # make user
        user_response = make_user(self)
        token = user_response["session"]["token"]

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        self.request.json_body = {"list_name": "foo1"}
        tasklists.tasklists(self.request)

        # Delete list
        self.request.method = 'DELETE'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["list_id is required"]}})

    def test_delete_task_list_by_id_different_user(self):
        # Make user one
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com",
                                  "user_pass": "TestPass"}
        user_response = users.users(self.request).json_body["d"]
        token = user_response["session"]["token"]

        # Create one list for user one
        self.request.method = 'POST'
        self.request.json_body = {"list_name": "foo1", "token": token}
        self.request.user = user(self.request)
        post_response = tasklists.tasklists(self.request).json_body["d"]
        list_id = post_response["list_id"]

        # Make user two
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "DifferentUser", "user_email": "test@squizzlezig.com",
                                  "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        token = post_response["session"]["token"]

        # Delete list
        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})
