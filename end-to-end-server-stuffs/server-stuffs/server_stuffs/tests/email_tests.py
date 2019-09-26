from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.models import ResetTokenModel, VerifyTokenModel
from server_stuffs.views import emails
from server_stuffs import user
from datetime import datetime, timedelta


class EmailTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_post_already_verified(self):
        # Make user
        user_data = self.make_user()
        user_email = user_data["user_email"]

        self.request.method = 'POST'
        self.request.json_body = {"user_email": user_email}

        self.request.user = user(self.request)
        response = emails.verifytokens(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user already verified"]}})

    def test_put_verify_user_email(self):
        # Make user
        user_data = self.make_user(email="success@simulator.amazonses.com", verified=False)
        user_id = user_data["user_id"]
        verify_token_data = self.make_verifytoken(user_id)

        # Verify user
        self.request.method = 'PUT'
        self.request.json_body = {"verifytoken": verify_token_data["token"]}

        self.request.user = user(self.request)
        response = emails.verifytokens(self.request)
        self.assertEqual(response.json_body, {"d": "user successfully verified"})

    def test_put_nonexistent_verify(self):
        # Verify user
        self.request.method = 'PUT'
        self.request.json_body = {"verifytoken": "nonexistentToken"}

        self.request.user = user(self.request)
        response = emails.verifytokens(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["verify token doesnt exist"]}})

    def test_put_verify_delete_old_tokens(self):
        # Make user
        user_data = self.make_user(email="success@simulator.amazonses.com", verified=False)
        user_id = user_data["user_id"]
        verify_token_data = self.make_verifytoken(user_id)

        # Make the first token invalid
        self.dbsession.query(VerifyTokenModel).filter(VerifyTokenModel.token == verify_token_data["token"]) \
            .update({VerifyTokenModel.started: datetime.utcnow() - timedelta(weeks=1)})

        verify_token_data = self.make_verifytoken(user_id)

        self.request.method = 'PUT'
        self.request.json_body = {"verifytoken": verify_token_data["token"]}

        self.request.user = user(self.request)
        response = emails.verifytokens(self.request)
        self.assertEqual(response.json_body, {"d": "user successfully verified"})

        verifytokens = self.dbsession.query(VerifyTokenModel).all()
        self.assertEqual(verifytokens, [])

    def test_post_send_password_reset(self):
        # Make user
        self.make_user(email="success@simulator.amazonses.com")

        self.request.method = 'POST'
        self.request.json_body = {"user_email": "success@simulator.amazonses.com"}
        response = emails.resettokens(self.request)
        self.assertEqual(response.json_body, {"d": "password reset email sent"})

    def test_post_reset_token_no_email(self):
        # Make user
        self.make_user()

        self.request.method = 'POST'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        response = emails.resettokens(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user_email is required"]}})

    def test_post_reset_token_nonexistent_user(self):
        self.request.method = 'POST'
        self.request.json_body = {"user_email": "nonexistent@jacob.squizzlezig.com"}
        response = emails.resettokens(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user doesnt exist"]}})

    def test_post_not_verified(self):
        # Make user
        user_data = self.make_user(verified=False)
        user_email = user_data["user_email"]

        self.request.method = 'POST'
        self.request.json_body = {"user_email": user_email}

        self.request.user = user(self.request)
        response = emails.resettokens(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user not verified"]}})

    def test_put_reset_successful(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]

        # Make reset token
        reset_token_data = self.make_resettoken(user_id)
        token = reset_token_data["token"]

        self.request.method = 'PUT'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {"resettoken": token, "user_pass": "different pass"}
        response = emails.resettokens(self.request)
        self.assertEqual(response.json_body, {"d": "password successfully reset"})

    def test_put_invalid_reset_token(self):
        # Make user
        user_data = self.make_user(email="success@simulator.amazonses.com")
        user_id = user_data["user_id"]

        # Make reset token
        reset_token = self.make_resettoken(user_id)

        # Make reset token invalid
        reset_token["started"] = datetime.utcnow() - timedelta(days=1)
        self.dbsession.query(ResetTokenModel).filter(ResetTokenModel.token == reset_token["token"]) \
            .update({ResetTokenModel.started: reset_token["started"]})

        self.request.method = 'PUT'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {"resettoken": reset_token["token"], "user_pass": "different pass"}
        response = emails.resettokens(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["reset token doesnt exist"]}})

    def test_put_nonexistent_reset_token(self):
        # Make user
        self.make_user()

        self.request.method = 'PUT'
        self.request.json_body = {"resettoken": "nonextistentToken"}
        response = emails.resettokens(self.request)
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
        response = emails.resettokens(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user_pass is required"]}})
