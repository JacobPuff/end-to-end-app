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
        post_response = make_user(self)
        user_id = post_response["user_id"]
        token = post_response["session"]["token"]

        # Get user
        self.request.method = 'GET'
        self.request.matchdict = {"user_id": user_id}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "testuser",
                                                    "user_email": "test@squizzlezig.com"}})

    def test_get_user_by_id_no_token(self):
        # Make user
        post_response = make_user(self)
        user_id = post_response["user_id"]

        # Get user
        self.request.method = 'GET'
        self.request.matchdict = {"user_id": user_id}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_user_by_id_no_user_id(self):
        # Make user
        post_response = make_user(self)
        token = post_response["session"]["token"]

        # Get user
        self.request.method = 'GET'
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_user_by_id_different_user(self):
        # Make user one
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        user_id = post_response["user_id"]

        # Make user two
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "DifferentUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        token = post_response["session"]["token"]

        # Get user
        self.request.method = 'GET'
        self.request.matchdict = {"user_id": user_id}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_put_user_by_id(self):
        # Make user
        post_response = make_user(self)
        token = post_response["session"]["token"]
        user_id = post_response["user_id"]

        # Update user
        self.request.method = 'PUT'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"user_name": "UserForTesting", "user_email": "testerino@squizzlezig.com",
                                  "user_pass": "passwordForTest", "token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "userfortesting",
                                                    "user_email": "testerino@squizzlezig.com"}})

    def test_put_user_by_id_no_token(self):
        # Make user
        post_response = make_user(self)
        user_id = post_response["user_id"]

        # Update user
        self.request.method = 'PUT'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"user_name": "UserForTesting", "user_email": "testerino@squizzlezig.com",
                                  "user_pass": "passwordForTest"}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_put_user_by_id_different_user(self):
        # Make user one
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        user_id = post_response["user_id"]

        # Make user two
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "DifferentUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        token = post_response["session"]["token"]

        # Update user
        self.request.method = 'PUT'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_put_user_by_id_nothing_provided(self):
        # Make user
        post_response = make_user(self)
        token = post_response["session"]["token"]
        user_id = post_response["user_id"]

        # Update user
        self.request.method = 'PUT'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["no values provided to update"]}})

    def test_delete_user_by_id(self):
        # Make user
        post_response = make_user(self)
        user_id = post_response["user_id"]
        token = post_response["session"]["token"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "deleted user " + str(user_id)})

    def test_delete_user_by_id_no_token(self):
        # Make user
        post_response = make_user(self)
        user_id = post_response["user_id"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.matchdict = {"user_id": user_id}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_delete_user_by_id_no_user_id(self):
        # Make user
        post_response = make_user(self)
        token = post_response["session"]["token"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_delete_user_by_id_different_user(self):
        # Make user one
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        user_id = post_response["user_id"]

        # Make user two
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "DifferentUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        post_response = users.users(self.request).json_body["d"]
        token = post_response["session"]["token"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})
