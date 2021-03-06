import transaction

from unittest import TestCase
from pyramid import testing
from sqlalchemy import create_engine
from uuid import uuid4
from server_stuffs.scripts.converters import dict_from_row
from server_stuffs.scripts.password_hashing import pwd_context
from server_stuffs.models.meta import Base
from server_stuffs.models import (
    UserModel,
    SessionModel,
    TaskListModel,
    TaskModel,
    ResetTokenModel,
    VerifyTokenModel,
    EmailBlacklistModel,
    get_session_factory,
    get_tm_session
)


engine = None
session = None

class TestBase(TestCase):
    """
    This makes everything required to interact with the devtest database for testing.
    """

    @classmethod
    def setUpClass(cls):
        global engine
        global session
        uri = 'postgresql://devtestuser:devtestpass@localhost:5432/devtest'
        engine = create_engine(uri)
        session = get_session_factory(engine)
        Base.metadata.create_all(engine)
        cls.class_dbsession = get_tm_session(get_session_factory(engine), transaction.manager)

    @classmethod
    def tearDownClass(cls):
        cls.class_dbsession.rollback()
        Base.metadata.drop_all(engine)

    def setUp(self):
        # This sets up a session per test
        self.dbsession = self.class_dbsession
        self.dbsession.begin_nested()

    def tearDown(self):
        self.dbsession.rollback()

    def make_user(self, username="TestUser", email="success@simulator.amazonses.com", password="TestPass", verified=True):
        # Make user
        new_user = UserModel()
        new_user.user_name = username.lower()
        new_user.user_email = email.lower()
        new_user.user_pass = pwd_context.hash(password)
        new_user.verified = verified

        # Put on user_id
        self.dbsession.add(new_user)
        self.dbsession.flush()
        self.dbsession.refresh(new_user)

        # Make session for the user
        new_session = self.make_session(new_user.user_id)

        returndict = dict_from_row(new_user)
        returndict["session"] = new_session
        return returndict

    def make_session(self, user_id):
        new_session = SessionModel()
        new_session.user_id = user_id
        new_session.token = str(uuid4())

        # Put on session_id
        self.dbsession.add(new_session)
        self.dbsession.flush()
        self.dbsession.refresh(new_session)

        returndict = dict_from_row(new_session)
        return returndict

    def make_list(self, list_name, user_id):
        # Make list
        new_list = TaskListModel()
        new_list.list_name = list_name
        new_list.user_id = user_id

        # Put on list_id
        self.dbsession.add(new_list)
        self.dbsession.flush()
        self.dbsession.refresh(new_list)

        returndict = dict_from_row(new_list)
        return returndict

    def make_task(self, list_id, task_name, task_done=False):
        # Make task
        new_task = TaskModel()
        new_task.list_id = list_id
        new_task.task_name = task_name
        new_task.task_done = task_done

        # Put on task_id
        self.dbsession.add(new_task)
        self.dbsession.flush()
        self.dbsession.refresh(new_task)

        returndict = dict_from_row(new_task)
        return returndict

    def make_resettoken(self, user_id):
        # Make resettoken
        new_resettoken = ResetTokenModel()
        new_resettoken.user_id = user_id
        new_resettoken.token = str(uuid4())

        # Put on ressettoken_id
        self.dbsession.add(new_resettoken)
        self.dbsession.flush()
        self.dbsession.refresh(new_resettoken)

        returndict = dict_from_row(new_resettoken)
        return returndict

    def make_verifytoken(self, user_id, temp_email=None):
        # Make verifytoken
        new_verifytoken = VerifyTokenModel()
        new_verifytoken.user_id = user_id
        new_verifytoken.temp_email = temp_email
        new_verifytoken.token = str(uuid4())

        # Put on verifytoken_id
        self.dbsession.add(new_verifytoken)
        self.dbsession.flush()
        self.dbsession.refresh(new_verifytoken)

        returndict = dict_from_row(new_verifytoken)
        return returndict

    def make_blacklisted_email(self, email="bounce@simulator.amazonses.com"):
        # Blacklist email
        new_blacklistedEmail = EmailBlacklistModel()
        new_blacklistedEmail.email = email

        # Add blacklisted email
        self.dbsession.add(new_blacklistedEmail)
        self.dbsession.flush()
        self.dbsession.refresh(new_blacklistedEmail)

        returndict = dict_from_row(new_blacklistedEmail)
        return returndict


class PyramidTestBase(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.dbsession = self.dbsession
        # Google only allows for success tests. Most tests wont care about reCaptcha
        # and setting it in the json_body would just take up space.

        # I cant add it to json_body because it will be overwritten when I set json_body in tests, so its here.
        # This also allows me to write better tests, because I can write my own stuff based on this.
        self.request.recaptchaTestToken = "successTestToken"
        
        # Tests dont get the config data, so Im setting to googles test secret here
        self.request.registry.settings["recaptcha_secret"] = '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe'

    def tearDown(self):
        testing.tearDown()
        TestBase.tearDown(self)
