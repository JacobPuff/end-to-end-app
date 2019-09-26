from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.models import ResetTokenModel, VerifyTokenModel
from server_stuffs.views import users
from server_stuffs import user
from datetime import datetime, timedelta


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
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@jacob.squizzlezig.com", "user_pass": "TestPass"}
        users.users(self.request)
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username already in use"]}})

    def test_post_user_with_short_pass(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@jacob.squizzlezig.com", "user_pass": "pass"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["password must be at least 8 characters"]}})

    def test_put_verify_user_email(self):
        # Make user
        user_data = self.make_user(email="success@simulator.amazonses.com", verified=False)
        user_id = user_data["user_id"]
        verify_token_data = self.make_verifytoken(user_id)

        # Verify user
        self.request.method = 'PUT'
        self.request.json_body = {"verifytoken": verify_token_data["token"]}

        self.request.user = user(self.request)
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": "user verified"})

    def test_put_nonexistent_verify(self):
        # Make user
        user_data = self.make_user(verified=False)

        # Verify user
        self.request.method = 'PUT'
        self.request.json_body = {"verifytoken": "nonexistentToken"}

        self.request.user = user(self.request)
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["verify token doesnt exist"]}})

    def test_put_verify_delete_old_tokens(self):
        # Make user
        user_data = self.make_user(email="success@simulator.amazonses.com", verified=False)
        user_id = user_data["user_id"]
        verify_token_data = self.make_verifytoken(user_id)

        # Make the first token invalid
        self.dbsession.query(VerifyTokenModel).filter(VerifyTokenModel.token == verify_token_data["token"])\
            .update({VerifyTokenModel.started: datetime.utcnow() - timedelta(weeks=1)})

        verify_token_data = self.make_verifytoken(user_id)

        self.request.method = 'PUT'
        self.request.json_body = {"verifytoken": verify_token_data["token"]}

        self.request.user = user(self.request)
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": "user verified"})

        verifytokens = self.dbsession.query(VerifyTokenModel).all()
        self.assertEqual(verifytokens, [])

    def test_put_send_password_reset(self):
        # Make user
        self.make_user(email="success@simulator.amazonses.com")

        self.request.method = 'PUT'
        self.request.json_body = {"user_email": "success@simulator.amazonses.com"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": "email sent"})

    def test_put_send_reset_successful(self):
        # Make user
        user_data = self.make_user(email="success@simulator.amazonses.com")
        user_id = user_data["user_id"]

        # Make reset token
        reset_token_data = self.make_resettoken(user_id)
        token = reset_token_data["token"]

        self.request.method = 'PUT'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {"resettoken": token, "user_pass": "different pass"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": "password successfully reset"})

    def test_put_invalid_reset_token(self):
        # Make user
        user_data = self.make_user(email="success@simulator.amazonses.com")
        user_id = user_data["user_id"]

        # Make reset token
        reset_token = self.make_resettoken(user_id)

        # Make reset token invalid
        reset_token["started"] = datetime.utcnow() - timedelta(days=1)
        self.dbsession.query(ResetTokenModel).filter(ResetTokenModel.token == reset_token["token"])\
            .update({ResetTokenModel.started: reset_token["started"]})

        self.request.method = 'PUT'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {"resettoken": reset_token["token"], "user_pass": "different pass"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["reset token doesnt exist"]}})

    def test_put_no_email(self):
        # Make user
        self.make_user()

        self.request.method = 'PUT'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user_email is required"]}})

    def test_put_nonexistent_user(self):
        self.request.method = 'PUT'
        self.request.json_body = {"user_email": "nonexistent@jacob.squizzlezig.com"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user doesnt exist"]}})

    def test_put_nonexistent_reset_token(self):
        # Make user
        self.make_user()

        self.request.method = 'PUT'
        self.request.json_body = {"resettoken": "nonextistentToken"}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["reset token doesnt exist"]}})

    def test_put_no_password_for_reset(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Make reset token
        reset_token_data = self.make_resettoken(user_id)
        token = reset_token_data["token"]

        self.request.method = 'PUT'
        self.request.json_body = {"resettoken": token}
        response = users.users(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user_pass is required"]}})

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
        user_data = self.make_user("differentUser")
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
        self.request.json_body = {"user_name": "UserForTesting", "user_email": "testerino@squizzlezig.com",
                                  "user_pass": "passwordForTest", "token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"user_id": user_id, "user_name": "userfortesting",
                                                    "user_email": "testerino@squizzlezig.com", "verified": True}})

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
        user_data = self.make_user("differentUser")
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
        user_data = self.make_user("differentUser")
        token = user_data["session"]["token"]

        # Delete user
        self.request.method = 'DELETE'
        self.request.matchdict = {"user_id": user_id}
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = users.users_by_id(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})
