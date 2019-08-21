from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.models import SessionModel, UserModel,  TaskListModel, TaskModel
from server_stuffs.views import sessions, users, tasklists, tasks
from server_stuffs import user
from datetime import datetime, timedelta
import json


class SessionTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_login_without_token_or_email(self):
        # Make user
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)
        session1 = response.json_body["d"]["session"]["session_id"]

        # Make user None so it actually logs in instead of using the token
        self.request.json_body = {}
        self.request.user = user(self.request)

        # Login without token or email
        self.request.json_body = {"user_name": "TestUser", "user_pass": "TestPass"}
        response = sessions.sessions(self.request)
        session2 = response.json_body["d"]["session_id"]
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session["session_id"],
                                                    "user_id": session["user_id"], "started": session["started"],
                                                    "last_active": session["last_active"], "token": session["token"]}})
        self.assertFalse(session1 == session2)

    def test_login_without_token_or_username(self):
        # Make user
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)
        sessionid1 = response.json_body["d"]["session"]["session_id"]

        # Make user None so it actually logs in instead of using the token
        self.request.json_body = {}
        self.request.user = user(self.request)

        # Login without token or username
        self.request.json_body = {"user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = sessions.sessions(self.request)
        sessionid2 = response.json_body["d"]["session_id"]
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session["session_id"],
                                                    "user_id": session["user_id"], "started": session["started"],
                                                    "last_active": session["last_active"], "token": session["token"]}})
        self.assertFalse(sessionid1 == sessionid2)

    def test_login_without_token_or_password(self):
        # Make user
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)

        # Make user None so it actually logs in instead of using the token
        self.request.json_body = {}
        self.request.user = user(self.request)

        # Login without token or username
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com"}
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["Username or email, and password needed"]}})

    def test_login_with_nothing_provided(self):
        # Make user
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)

        # Make json_body an empty dict so nothing is provided, and user is None
        self.request.json_body = {}
        self.request.user = user(self.request)

        # Login with nothing provided
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["Username or email, and password needed"]}})

    def test_login_with_token(self):
        # Make user
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)
        self.request.json_body = {"token": response.json_body["d"]["session"]["token"]}
        self.request.user = user(self.request)

        # Login with good token
        response = sessions.sessions(self.request)
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session["session_id"],
                                                    "user_id": session["user_id"], "started": session["started"],
                                                    "last_active": session["last_active"], "token": session["token"]}})

    def test_login_with_bad_token(self):
        # Make user
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)
        session = response.json_body["d"]["session"]

        # make token invalid
        session["last_active"] = datetime.utcnow() - timedelta(weeks=1, days=1)
        self.request.dbsession.query(SessionModel).filter(SessionModel.token == session["token"])\
            .update({SessionModel.last_active: session["last_active"]})

        # check invalid
        self.request.json_body = {"token": session["token"]}
        self.request.user = user(self.request)
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["Username or email, and password needed"]}})

    def test_check_token_valid_put(self):
        # Make user
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)
        self.request.user = response.json_body["d"]

        # check valid
        self.request.json_body = {"token":  self.request.user["session"]["token"]}
        response = sessions.sessions(self.request)
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session["session_id"],
                                                    "user_id": session["user_id"], "started": session["started"],
                                                    "last_active": session["last_active"], "token": session["token"]}})

    def test_session_delete(self):
        # Make user
        self.request.method = 'POST'
        self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
        response = users.users(self.request)
        self.request.user = response.json_body["d"]

        session = self.request.user["session"]
        self.request.method = 'DELETE'
        self.request.json_body = {"token": session["token"]}
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": "deleted session"})
