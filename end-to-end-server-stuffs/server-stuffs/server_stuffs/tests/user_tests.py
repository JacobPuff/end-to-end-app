from server_stuffs.scripts.test_reuse import PyramidTestBase
from server_stuffs.models import tasklistmodel, taskmodel, usermodel
from server_stuffs.views import tasklists, tasks, users


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
        # YO DAWG THIS IS WHAT YOU WERE WORKING ON! YOU JUST WANT TO RETURN THE USER!
        # Like if you just had a session with the user_id and the token or something
        # I dunno, its preparing for the future
        self.request.method = 'GET'
        self.request.json_body = {"token"}
        return
