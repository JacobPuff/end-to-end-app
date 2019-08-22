from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.models import SessionModel, UserModel,  TaskListModel, TaskModel
from server_stuffs.views import sessions, users, tasklists, tasks
from server_stuffs import user
from datetime import datetime, timedelta


def make_user(self):
    self.request.method = 'POST'
    self.request.json_body = {"user_name": "TestUser", "user_email": "test@squizzlezig.com", "user_pass": "TestPass"}
    response = users.users(self.request)
    return response.json_body["d"]


class SessionTests(PyramidTestBase):

    def setUp(self):
        PyramidTestBase.setUp(self)

    def tearDown(self):
        PyramidTestBase.tearDown(self)

    def test_login_without_token_or_email(self):
        # Make user
        user_response = make_user(self)
        session1 = user_response["session"]["session_id"]

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
        user_response = make_user(self)
        sessionid1 = user_response["session"]["session_id"]

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
        make_user(self)

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
        make_user(self)

        # Make json_body an empty dict so nothing is provided, and user is None
        self.request.json_body = {}
        self.request.user = user(self.request)

        # Login with nothing provided
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": {"error_type": "api_error",
                                                    "errors": ["Username or email, and password needed"]}})

    def test_login_with_token(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        # Login with good token
        response = sessions.sessions(self.request)
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session["session_id"],
                                                    "user_id": session["user_id"], "started": session["started"],
                                                    "last_active": session["last_active"], "token": session["token"]}})

    def test_login_with_bad_token(self):
        # Make user
        user_response = make_user(self)
        session = user_response["session"]

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
        user_response = make_user(self)
        self.request.json_body = {"token":  user_response["session"]["token"]}
        self.request.user = user(self.request)

        # check valid
        response = sessions.sessions(self.request)
        session = response.json_body["d"]
        self.assertEqual(response.json_body, {"d": {"session_id": session["session_id"],
                                                    "user_id": session["user_id"], "started": session["started"],
                                                    "last_active": session["last_active"], "token": session["token"]}})

    def test_session_delete(self):
        # Make user
        user_response = make_user(self)
        self.request.json_body = {"token": user_response["session"]["token"]}
        self.request.user = user(self.request)

        self.request.method = 'DELETE'
        response = sessions.sessions(self.request)
        self.assertEqual(response.json_body, {"d": "deleted session"})
