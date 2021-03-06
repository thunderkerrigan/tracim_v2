# -*- coding: utf-8 -*-
import unittest

import plaster
import requests
import transaction
from depot.manager import DepotManager
from pyramid import testing
from sqlalchemy.exc import IntegrityError

from tracim_backend.lib.core.content import ContentApi
from tracim_backend.lib.core.workspace import WorkspaceApi
from tracim_backend.models import get_engine
from tracim_backend.models import DeclarativeBase
from tracim_backend.models import get_session_factory
from tracim_backend.models import get_tm_session
from tracim_backend.models.contents import CONTENT_TYPES
from tracim_backend.models.data import Workspace
from tracim_backend.models.data import ContentRevisionRO
from tracim_backend.models.data import Content
from tracim_backend.lib.utils.logger import logger
from tracim_backend.fixtures import FixturesLoader
from tracim_backend.fixtures.users_and_groups import Base as BaseFixture
from tracim_backend.config import CFG
from tracim_backend.extensions import hapic
from tracim_backend import web
from webtest import TestApp
from io import BytesIO
from PIL import Image


def eq_(a, b, msg=None):
    # TODO - G.M - 05-04-2018 - Remove this when all old nose code is removed
    assert a == b, msg or "%r != %r" % (a, b)

# TODO - G.M - 2018-06-179 - Refactor slug change function
#  as a kind of pytest fixture ?


def set_html_document_slug_to_legacy(session_factory) -> None:
    """
    Simple function to help some functional test. This modify "html-documents"
    type content in database to legacy "page" slug.
    :param session_factory: session factory of the test
    :return: Nothing.
    """
    dbsession = get_tm_session(
        session_factory,
        transaction.manager
    )
    content_query = dbsession.query(ContentRevisionRO).filter(ContentRevisionRO.type == 'page').filter(ContentRevisionRO.content_id == 6)  # nopep8
    assert content_query.count() == 0
    html_documents_query = dbsession.query(ContentRevisionRO).filter(ContentRevisionRO.type == 'html-document')  # nopep8
    html_documents_query.update({ContentRevisionRO.type: 'page'})
    transaction.commit()
    assert content_query.count() > 0


def create_1000px_png_test_image():
    file = BytesIO()
    image = Image.new('RGBA', size=(1000, 1000), color=(0, 0, 0))
    image.save(file, 'png')
    file.name = 'test_image.png'
    file.seek(0)
    return file


class FunctionalTest(unittest.TestCase):

    fixtures = [BaseFixture]
    config_uri = 'tests_configs.ini'
    config_section = 'functional_test'

    def setUp(self):
        logger._logger.setLevel('WARNING')

        DepotManager._clear()
        self.settings = plaster.get_settings(
            self.config_uri,
            self.config_section
        )
        hapic.reset_context()
        self.engine = get_engine(self.settings)
        DeclarativeBase.metadata.create_all(self.engine)
        self.session_factory = get_session_factory(self.engine)
        self.app_config = CFG(self.settings)
        self.app_config.configure_filedepot()
        self.init_database(self.settings)
        DepotManager._clear()
        self.run_app()

    def run_app(self):
        app = web({}, **self.settings)
        self.testapp = TestApp(app)

    def init_database(self, settings):
        with transaction.manager:
            dbsession = get_tm_session(self.session_factory, transaction.manager)
            try:
                fixtures_loader = FixturesLoader(dbsession, self.app_config)
                fixtures_loader.loads(self.fixtures)
                transaction.commit()
                print("Database initialized.")
            except IntegrityError:
                print('Warning, there was a problem when adding default data'
                      ', it may have already been added:')
                import traceback
                print(traceback.format_exc())
                transaction.abort()
                print('Database initialization failed')

    def tearDown(self):
        logger.debug(self, 'TearDown Test...')
        from tracim_backend.models.meta import DeclarativeBase

        testing.tearDown()
        transaction.abort()
        DeclarativeBase.metadata.drop_all(self.engine)
        DepotManager._clear()


class FunctionalTestEmptyDB(FunctionalTest):
    fixtures = []


class FunctionalTestNoDB(FunctionalTest):
    config_section = 'functional_test_no_db'

    def init_database(self, settings):
        self.engine = get_engine(settings)


class CommandFunctionalTest(FunctionalTest):

    def run_app(self):
        self.session = get_tm_session(self.session_factory, transaction.manager)


class BaseTest(unittest.TestCase):
    """
    Pyramid default test.
    """

    config_uri = 'tests_configs.ini'
    config_section = 'base_test'

    def setUp(self):
        logger._logger.setLevel('WARNING')
        logger.debug(self, 'Setup Test...')
        self.settings = plaster.get_settings(
            self.config_uri,
            self.config_section
        )
        self.config = testing.setUp(settings = self.settings)
        self.config.include('tracim_backend.models')
        DepotManager._clear()
        DepotManager.configure(
            'test', {'depot.backend': 'depot.io.memory.MemoryFileStorage'}
        )
        settings = self.config.get_settings()
        self.app_config = CFG(settings)
        from tracim_backend.models import (
            get_engine,
            get_session_factory,
            get_tm_session,
        )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.session = get_tm_session(session_factory, transaction.manager)
        self.init_database()

    def init_database(self):
        logger.debug(self, 'Init Database Schema...')
        from tracim_backend.models.meta import DeclarativeBase
        DeclarativeBase.metadata.create_all(self.engine)

    def tearDown(self):
        logger.debug(self, 'TearDown Test...')
        from tracim_backend.models.meta import DeclarativeBase

        testing.tearDown()
        transaction.abort()
        DeclarativeBase.metadata.drop_all(self.engine)


class StandardTest(BaseTest):
    """
    BaseTest with default fixtures
    """
    fixtures = [BaseFixture]

    def init_database(self):
        BaseTest.init_database(self)
        fixtures_loader = FixturesLoader(
            session=self.session,
            config=CFG(self.config.get_settings()))
        fixtures_loader.loads(self.fixtures)


class DefaultTest(StandardTest):

    def _create_workspace_and_test(self, name, user) -> Workspace:
        """
        All extra parameters (*args, **kwargs) are for Workspace init
        :return: Created workspace instance
        """
        WorkspaceApi(
            current_user=user,
            session=self.session,
            config=self.app_config,
        ).create_workspace(name, save_now=True)

        eq_(
            1,
            self.session.query(Workspace).filter(
                Workspace.label == name
            ).count()
        )
        return self.session.query(Workspace).filter(
            Workspace.label == name
        ).one()

    def _create_content_and_test(
            self,
            name,
            workspace,
            *args,
            **kwargs
    ) -> Content:
        """
        All extra parameters (*args, **kwargs) are for Content init
        :return: Created Content instance
        """
        content = Content(*args, **kwargs)
        content.label = name
        content.workspace = workspace
        self.session.add(content)
        self.session.flush()

        content_api = ContentApi(
            current_user=None,
            session=self.session,
            config=self.app_config,
        )
        eq_(
            1,
            content_api.get_canonical_query().filter(
                Content.label == name
            ).count()
        )
        return content_api.get_canonical_query().filter(
            Content.label == name
        ).one()

    def _create_thread_and_test(self,
                                user,
                                workspace_name='workspace_1',
                                folder_name='folder_1',
                                thread_name='thread_1') -> Content:
        """
        :return: Thread
        """
        workspace = self._create_workspace_and_test(workspace_name, user)
        folder = self._create_content_and_test(
            folder_name, workspace,
            type=CONTENT_TYPES.Folder.slug,
            owner=user
        )
        thread = self._create_content_and_test(
            thread_name,
            workspace,
            type=CONTENT_TYPES.Thread.slug,
            parent=folder,
            owner=user
        )
        return thread


class MailHogTest(DefaultTest):
    """
    Theses test need a working mailhog
    """

    config_section = 'mail_test'

    def tearDown(self):
        logger.debug(self, 'Cleanup MailHog list...')
        requests.delete('http://127.0.0.1:8025/api/v1/messages')
