from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.models import SessionModel
from server_stuffs.views import sessions
from server_stuffs import user
from datetime import datetime, timedelta



class SessionTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_login_without_token_or_email(self):
        # Make user
        user_data = self.make_user()
        sessionid1 = user_data["session"]["session_id"]

        # Login without token or email
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_pass": "TestPass"}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session.get("session_id"),
                                                    "user_id": session.get("user_id"),
                                                    "started": session.get("started"),
                                                    "last_active": session.get("last_active"),
                                                    "token": session.get("token")}})
        sessionid2 = session["session_id"]
        self.assertFalse(sessionid1 == sessionid2)

    def test_login_without_token_or_username(self):
        # Make user
        user_data = self.make_user()
        sessionid1 = user_data["session"]["session_id"]

        # Login without token or username
        self.request.method = 'POST'
        self.request.json_body = {"user_email": "test@jacob.squizzlezig.com", "user_pass": "TestPass"}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session.get("session_id"),
                                                    "user_id": session.get("user_id"),
                                                    "started": session.get("started"),
                                                    "last_active": session.get("last_active"),
                                                    "token": session.get("token")}})
        sessionid2 = session["session_id"]
        self.assertFalse(sessionid1 == sessionid2)

    def test_login_without_token_or_password(self):
        # Make user
        self.make_user()

        # Login without token or password
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@jacob.squizzlezig.com"}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username or email, and password are required"]}})

    def test_login_with_wrong_password(self):
        # Make user
        self.make_user()

        # Login with wrong password
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_pass": "WrongPass"}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["user doesnt exist"]}})

    def test_login_with_nothing_provided(self):
        # Make user
        self.make_user()

        # Login with nothing provided
        self.request.method = 'POST'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username or email, and password are required"]}})

    def test_login_with_token(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # Login with good token
        self.request.method = 'POST'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session.get("session_id"),
                                                    "user_id": session.get("user_id"),
                                                    "started": session.get("started"),
                                                    "last_active": session.get("last_active"),
                                                    "token": session.get("token")}})

    def test_login_with_bad_token(self):
        # Make user
        user_data = self.make_user()
        session = user_data["session"]

        # make token invalid
        session["last_active"] = datetime.utcnow() - timedelta(weeks=1, days=1)
        self.dbsession.query(SessionModel).filter(SessionModel.token == session["token"])\
            .update({SessionModel.last_active: session["last_active"]})

        # check invalid
        self.request.method = 'POST'
        self.request.json_body = {"token": session["token"]}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["username or email, and password are required"]}})

    def test_check_token_valid_put(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        # check valid
        self.request.method = 'PUT'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session["session_id"],
                                                    "user_id": session["user_id"], "started": session["started"],
                                                    "last_active": session["last_active"], "token": session["token"]}})

    def test_check_token_valid_put_no_token(self):
        # Make user
        self.make_user()

        # check valid
        self.request.method = 'PUT'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

    def test_check_token_valid_put_deletes_all_invalid_tokens(self):
        # Make user
        user_data = self.make_user()
        user_id = user_data["user_id"]
        session1 = user_data["session"]

        # Create second session
        session2token = self.make_session(user_id)["token"]

        # Make first token invalid
        session1["last_active"] = datetime.utcnow() - timedelta(weeks=1, days=1)
        self.dbsession.query(SessionModel).filter(SessionModel.token == session1["token"]) \
            .update({SessionModel.last_active: session1["last_active"]})

        # check first token invalid
        self.request.method = 'PUT'
        self.request.json_body = {"token": session1["token"]}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})

        # check second token valid
        self.request.method = 'PUT'
        self.request.json_body = {"token": session2token}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        session2 = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session2.get("session_id"),
                                                    "user_id": session2.get("user_id"),
                                                    "started": session2.get("started"),
                                                    "last_active": session2.get("last_active"),
                                                    "token": session2.get("token")}})

        # check invalid token deleted
        session1Exists = self.dbsession.query(SessionModel)\
            .filter(SessionModel.token == session1["token"]).one_or_none()

        self.assertEqual(session1Exists, None)

    def test_session_delete(self):
        # Make user
        user_data = self.make_user()
        token = user_data["session"]["token"]

        self.request.method = 'DELETE'
        self.request.json_body = {"token": token}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": "deleted session"})

    def test_session_delete_no_token(self):
        # Make user
        self.make_user()

        self.request.method = 'DELETE'
        # This needs to be set because DummyRequest doesnt actually have a json_body attribute
        self.request.json_body = {}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["not authenticated for this request"]}})
