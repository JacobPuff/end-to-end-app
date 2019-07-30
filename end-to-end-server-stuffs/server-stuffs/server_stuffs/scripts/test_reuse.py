import transaction

from unittest import TestCase
from pyramid import testing, request
from sqlalchemy import create_engine
from server_stuffs.models.meta import Base
from server_stuffs.models import (
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


class PyramidTestBase(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        self.config = testing.setUp()
        self.request = testing.DummyRequest()
        self.request.dbsession = self.dbsession

    def tearDown(self):
        testing.tearDown()
        TestBase.tearDown(self)
