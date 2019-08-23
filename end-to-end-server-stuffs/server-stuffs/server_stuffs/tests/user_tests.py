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
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "testuser",
                                                    "user_email": "test@squizzlezig.com", "session": session}})

    def test_post_user_no_password(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username, email, and password are required"]}})

    def test_post_user_no_username_or_email(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_pass": "TestPass"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username, email, and password are required"]}})

    def test_post_user_nothing_provided(self):
        self.request.method = 'POST'
        self.request.json_body = {}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username, email, and password are required"]}})

    def test_post_user_with_duplicate_username(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        users.users(self.request)
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username already in use"]}})

    def test_post_user_with_short_pass(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "pass"}
        users.users(self.request)
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["password must be at least 8 characters"]}})

    def test_get_user_by_id(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        # Get user
        user_id = user_response["user_id"]
        self.request.matchdict = {"user_id": user_id}
        self.request.method = 'GET'
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "testuser",
                                                    "user_email": "test@squizzlezig.com"}})

    def test_put_user_by_id(self):
        # Make user
        user_response = make_user(self)
        token = user_response["session"]["token"]
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)

        # Update user
        user_id = user_response["user_id"]
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"user_name": "UserForTesting", "user_email": "testerino@squizzlezig.com",
                                  "user_pass": "passwordForTest", "token": token}
        self.request.method = 'PUT'
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "userfortesting",
                                                    "user_email": "testerino@squizzlezig.com"}})

    def test_delete_user_by_id(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        # Delete user
        user_id = user_response["user_id"]
        self.request.matchdict = {"user_id": str(user_id)}
        self.request.method = 'DELETE'
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "deleted user " + str(user_id)})
