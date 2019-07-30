# -*- coding: utf-8 -*-
from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.views import tasklists
import json

class TaskListTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_get_all_task_lists(self):
        list_ids = []
        # Create all the task lists
        self.request.method = 'POST'
        self.request.body = '{"user_id": 1, "list_name": "foo1"}'
        post_response = tasklists.tasklists(self.request)
        list_ids.append(json.loads(post_response.body)["d"]["list_id"])

        self.request.body = '{"user_id": 1, "list_name": "bar2"}'
        post_response = tasklists.tasklists(self.request)
        list_ids.append(json.loads(post_response.body)["d"]["list_id"])

        # Get all the task lists
        self.request.method = 'GET'
        self.request.body = None
        response = tasklists.tasklists(self.request)
        self.assertEqual(response.body, b'{"d": [{"list_id": '+bytes(str(list_ids[0]), "utf-8")+b', "user_id": 1, "list_name": "foo1"}, '+
            b'{"list_id": '+bytes(str(list_ids[1]), "utf-8")+b', "user_id": 1, "list_name": "bar2"}]}')

    def test_post_task_list(self):
        self.request.method = 'POST'
        self.request.body = '{"user_id": 1, "list_name": "foo1"}'
        response = tasklists.tasklists(self.request)
        response_body = json.loads(response.body)
        list_id = response_body["d"]["list_id"]
        self.assertEqual(response.body, b'{"d": {"list_id": '+bytes(str(list_id), "utf-8")+b', "user_id": 1, "list_name": "foo1"}}')

    def test_get_tasklist_by_id(self):
        # Create one list
        self.request.method = 'POST'
        self.request.body = '{"user_id": 1, "list_name": "foo1"}'
        post_response = tasklists.tasklists(self.request)
        list_id = json.loads(post_response.body)["d"]["list_id"]

        # Get one list
        self.request.method = 'GET'
        self.request.matchdict = {"list_id": list_id}
        get_response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(get_response.body, b'{"d": {"list_id": '+bytes(str(list_id), "utf-8")+b', "user_id": 1, "list_name": "foo1"}}')

    def test_put_tasklist_by_id(self):
        self.request.method = 'POST'
        self.request.body = '{"user_id": 1, "list_name": "foo1"}'
        post_response = tasklists.tasklists(self.request)
        list_id = json.loads(post_response.body)["d"]["list_id"]

        self.request.method = 'PUT'
        self.request.matchdict = {"list_id": list_id}
        self.request.body = '{"user_id": 1, "list_name": "put foo1"}'
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.body, b'task list '+bytes(str(list_id), 'utf-8')+b' updated')

    def test_delete_tasklist_by_id(self):
        self.request.method = 'POST'
        self.request.body = '{"user_id": 1, "list_name": "foo1"}'
        post_response = tasklists.tasklists(self.request)
        list_id = json.loads(post_response.body)["d"]["list_id"]

        self.request.method = 'DELETE'
        self.request.matchdict = {"list_id": list_id}
        response = tasklists.tasklists_by_id(self.request)
        self.assertEqual(response.body, b'task list '+bytes(str(list_id), "utf-8")+b' deleted')