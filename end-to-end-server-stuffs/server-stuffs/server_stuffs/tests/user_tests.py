from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.models import UserModel
from server_stuffs.scripts.converters import array_of_dicts_from_array_of_models
from server_stuffs.views import users
from server_stuffs import user


class UserTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_post_user(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "success@simulator.amazonses.com", "user_pass": "TestPass"}
        response = users.users(self.request)
        user_id = response.json_body["d"]["user_id"]
        session = response.json_body["d"]["session"]
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "testuser",
                                                    "user_email": "success@simulator.amazonses.com", "session": session,
                                                    "verified": False}})

    def test_post_user_no_password(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@jacob.squizzlezig.com"}
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
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username, email, and password are required"]}})

    def test_post_user_with_duplicate_username(self):
        self.make_user()
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "differentemail@jacob.squizzlezig.com",
                                  "user_pass": "TestPass"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username already in use"]}})

    def test_post_user_with_duplicate_email_verified(self):
        self.make_user()
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "DifferentUsername", "user_email": "test@jacob.squizzlezig.com",
                                  "user_pass": "TestPass"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["email already in use"]}})
    
    def test_post_user_with_duplicate_email_not_verified(self):
        user_data = self.make_user(email="success@simulator.amazonses.com", verified=False)
        user_id = user_data["user_id"]
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "Differentusername", "user_email": "success@simulator.amazonses.com",
                                  "user_pass": "passwordForTest"}
        response = users.users(self.request)
        session = response.json_body["d"]["session"]
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "differentusername",
                                                    "user_email": "success@simulator.amazonses.com", "session": session,
                                                    "verified": False}})

    def test_post_user_with_short_pass(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@jacob.squizzlezig.com", "user_pass": "pass"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["password must be at least 8 characters"]}})

    def test_get_user_by_id(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Get user
        self.request.method = 'GET'
        self.request.matchdict = {"user_id": user_id}
        self.request.GET = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "testuser",
                                                    "user_email": "test@jacob.squizzlezig.com", "verified": True}})

    def test_get_user_by_id_no_token(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Get user
        self.request.method = 'GET'
        self.request.matchdict = {"user_id": user_id}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_get_user_by_id_no_user_id(self):
        # Make user
        post_response = self.make_user()
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
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Make user two
        user_data = self.make_user("differentUser", "differentEmail@jacob.squizzlezig.com")
        token = user_data["session"]["token"]

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
        user_data = self.make_user()
        token = user_data["session"]["token"]
        user_id = user_data["user_id"]

        # Update user
        self.request.method = 'PUT'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"user_name": "UserForTesting", "user_email": "success@simulator.amazonses.com",
                                  "old_pass": "TestPass", "user_pass": "passwordForTest", "token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "userfortesting",
                                                    "user_email": "test@jacob.squizzlezig.com", "verified": True}})

    def test_put_user_by_id_no_old_pass(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]
        user_id = user_data["user_id"]

        # Update user
        self.request.method = 'PUT'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"user_name": "UserForTesting", "user_email": "testerino@squizzlezig.com",
                                  "user_pass": "passwordForTest", "token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["old_pass required when updating password"]}})

    def test_put_user_by_id_no_new_pass(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]
        user_id = user_data["user_id"]

        # Update user
        self.request.method = 'PUT'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"user_name": "UserForTesting", "user_email": "testerino@squizzlezig.com",
                                  "old_pass": "TestPass", "token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user_pass required when using old_pass"]}})
    
    def test_put_user_by_id_different_old_pass(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]
        user_id = user_data["user_id"]

        # Update user
        self.request.method = 'PUT'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"user_name": "UserForTesting", "user_email": "testerino@squizzlezig.com",
                                  "old_pass": "WrongOldPass", "user_pass": "passwordForTest", "token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["old_pass didnt match"]}})

    def test_put_user_by_id_no_token(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]

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
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Make user two
        user_data = self.make_user("differentUser", "differentEmail@jacob.squizzlezig.com")
        token = user_data["session"]["token"]

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
        user_data = self.make_user()
        token = user_data["session"]["token"]
        user_id = user_data["user_id"]

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
        user_data = self.make_user()
        user_id = user_data["user_id"]
        token = user_data["session"]["token"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": "deleted user " + str(user_id)})

    def test_delete_user_by_id_no_token(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.matchdict = {"user_id": user_id}
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_delete_user_by_id_no_user_id(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_delete_user_by_id_different_user(self):
        # Make user one
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Make user two
        user_data = self.make_user("differentUser", "differentEmail@jacob.squizzlezig.com")
        token = user_data["session"]["token"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})
