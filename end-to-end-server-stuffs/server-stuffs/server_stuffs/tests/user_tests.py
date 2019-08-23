from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.models import tasklistmodel, taskmodel, usermodel
from server_stuffs.views import tasklists, tasks, users
from server_stuffs import user


def make_user(self):
    self.request.method = 'POST'
    self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
    response = users.users(self.request)
    return response.json_body["d"]


class UserTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_post_user(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)
        user_id = response.json_body["d"]["user_id"]
        session = response.json_body["d"]["session"]
        self.assertEqual(response.json_body, {"d": {"user_id":  user_id, "user_name": "testuser",
                                                    "user_email": "test@squizzlezig.com", "session": session}})

    def test_get_user_by_id(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        # Get user
        user_id = user_response["user_id"]
        self.request.matchdict = {"user_id": str(user_id)}
        self.request.method = 'GET'
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "testuser",
                                                    "user_email": "test@squizzlezig.com"}})

    def test_delete_user_by_id(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        # Get user
        user_id = user_response["user_id"]
        self.request.matchdict = {"user_id": str(user_id)}
        self.request.method = 'DELETE'
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "deleted user " + str(user_id)})
