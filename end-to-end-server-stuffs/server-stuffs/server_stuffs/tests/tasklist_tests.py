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
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        # Create all the task lists
        self.request.method = 'POST'
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "foo1"}
        post_response = tasklists.tasklists(self.request)
        list_ids.append(post_response.json_body["d"]["list_id"])

        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "bar2"}
        post_response = tasklists.tasklists(self.request)
        list_ids.append(post_response.json_body["d"]["list_id"])

        # Get all the task lists
        self.request.method = 'GET'
        self.request.json_body = None
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.json_body, {"d": [{"list_id": list_ids[0], "user_id": user_response["user_id"], "list_name": "foo1"},
                                               {"list_id": list_ids[1],"user_id": user_response["user_id"], "list_name": "bar2"}]})

    def test_post_task_list(self):
        # make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "foo1"}
        response = tasklists.tasklists(self.request)
        list_id = response.json_body["d"]["list_id"]
        self.assertEqual(response.json_body, {"d": {"list_id": list_id, "user_id": user_response["user_id"], "list_name": "foo1"}})

    def test_get_tasklist_by_id(self):
        # make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        # Create one list
        self.request.method = 'POST'
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "foo1"}
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        # Get one list
        self.request.method = 'GET'
        self.request.matchdict = {"list_id": list_id}
        get_response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(get_response.json_body, {"d": {"list_id": list_id, "user_id": user_response["user_id"], "list_name": "foo1"}})

    def test_put_tasklist_by_id(self):
        # make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "foo1"}
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        self.request.method = 'PUT'
        self.request.matchdict = {"list_id": list_id}
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "put foo1"}
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task list " + str(list_id) + " updated"})

    def test_delete_tasklist_by_id(self):
        # make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'POST'
        self.request.json_body = {"user_id": user_response["user_id"], "list_name": "foo1"}
        post_response = tasklists.tasklists(self.request)
        list_id = post_response.json_body["d"]["list_id"]

        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "task list " + str(list_id) + " deleted"})
