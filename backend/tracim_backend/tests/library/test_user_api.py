# -*- coding: utf-8 -*-
import pytest
import transaction
from tracim_backend import models

from tracim_backend.exceptions import AuthenticationFailed
from tracim_backend.exceptions import TooShortAutocompleteString
from tracim_backend.exceptions import UserDoesNotExist
from tracim_backend.exceptions import UserNotActive
from tracim_backend.lib.core.group import GroupApi
from tracim_backend.lib.core.user import UserApi
from tracim_backend.lib.core.userworkspace import RoleApi
from tracim_backend.lib.core.workspace import WorkspaceApi
from tracim_backend.models import User
from tracim_backend.models.context_models import UserInContext
from tracim_backend.models.data import UserRoleInWorkspace
from tracim_backend.tests import DefaultTest
from tracim_backend.tests import eq_


class TestUserApi(DefaultTest):

    def test_unit__create_minimal_user__ok__nominal_case(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u = api.create_minimal_user('bob@bob')
        assert u.email == 'bob@bob'
        assert u.display_name == 'bob'

    def test_unit__create_minimal_user_and_update__ok__nominal_case(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u = api.create_minimal_user('bob@bob')
        api.update(u, 'bob', 'bob@bob', 'pass', do_save=True)
        nu = api.get_one_by_email('bob@bob')
        assert nu is not None
        assert nu.email == 'bob@bob'
        assert nu.display_name == 'bob'
        assert nu.validate_password('pass')

    def test__unit__create__user__ok_nominal_case(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u = api.create_user(
            email='bob@bob',
            password='pass',
            name='bob',
            timezone='+2',
            do_save=True,
            do_notify=False,
        )
        assert u is not None
        assert u.email == "bob@bob"
        assert u.validate_password('pass')
        assert u.display_name == 'bob'
        assert u.timezone == '+2'

    def test_unit__user_with_email_exists__ok__nominal_case(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u = api.create_minimal_user('bibi@bibi')
        api.update(u, 'bibi', 'bibi@bibi', 'pass', do_save=True)
        transaction.commit()

        eq_(True, api.user_with_email_exists('bibi@bibi'))
        eq_(False, api.user_with_email_exists('unknown'))

    def test_get_one_by_email(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u = api.create_minimal_user('bibi@bibi')
        self.session.flush()
        api.update(u, 'bibi', 'bibi@bibi', 'pass', do_save=True)
        uid = u.user_id
        transaction.commit()

        eq_(uid, api.get_one_by_email('bibi@bibi').user_id)

    def test_unit__get_one_by_email__err__user_does_not_exist(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        with pytest.raises(UserDoesNotExist):
            api.get_one_by_email('unknown')

    def test_unit__get_all__ok__nominal_case(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u1 = api.create_minimal_user('bibi@bibi')

        users = api.get_all()
        # u1 + Admin user from BaseFixture
        assert 2 == len(users)

    def test_unit__get_known__user__admin__too_short_acp_str(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u1 = api.create_user(
            email='email@email',
            name='name',
            do_notify=False,
            do_save=True,
        )
        with pytest.raises(TooShortAutocompleteString):
            api.get_known_user('e')

    def test_unit__get_known__user__admin__by_email(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u1 = api.create_user(
            email='email@email',
            name='name',
            do_notify=False,
            do_save=True,
        )

        users = api.get_known_user('email')
        assert len(users) == 1
        assert users[0] == u1

    def test_unit__get_known__user__user__no_workspace_empty_known_user(self):
        admin = self.session.query(models.User) \
            .filter(models.User.email == 'admin@admin.admin') \
            .one()
        api = UserApi(
            current_user=admin,
            session=self.session,
            config=self.config,
        )
        u1 = api.create_user(
            email='email@email',
            name='name',
            do_notify=False,
            do_save=True,
        )
        api2 = UserApi(
            current_user=u1,
            session=self.session,
            config=self.config,
        )
        users = api2.get_known_user('email')
        assert len(users) == 0

    def test_unit__get_known__user__same_workspaces_users_by_name(self):
        admin = self.session.query(models.User) \
            .filter(models.User.email == 'admin@admin.admin') \
            .one()
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u1 = api.create_user(
            email='email@email',
            name='name',
            do_notify=False,
            do_save=True,
        )
        u2 = api.create_user(
            email='email2@email2',
            name='name2',
            do_notify=False,
            do_save=True,
        )
        u3 = api.create_user(
            email='notfound@notfound',
            name='notfound',
            do_notify=False,
            do_save=True,
        )
        wapi = WorkspaceApi(
            current_user=admin,
            session=self.session,
            config=self.app_config,
        )
        workspace = wapi.create_workspace(
            'test workspace n°1',
            save_now=True)
        role_api = RoleApi(
            current_user=admin,
            session=self.session,
            config=self.app_config,
        )
        role_api.create_one(u1, workspace, UserRoleInWorkspace.READER, False)
        role_api.create_one(u2, workspace, UserRoleInWorkspace.READER, False)
        role_api.create_one(u3, workspace, UserRoleInWorkspace.READER, False)
        api2 = UserApi(
            current_user=u1,
            session=self.session,
            config=self.config,
        )
        users = api2.get_known_user('name')
        assert len(users) == 2
        assert users[0] == u1
        assert users[1] == u2

    def test_unit__get_known__user__same_workspaces_users_by_email(self):
        admin = self.session.query(models.User) \
            .filter(models.User.email == 'admin@admin.admin') \
            .one()
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u1 = api.create_user(
            email='email@email',
            name='name',
            do_notify=False,
            do_save=True,
        )
        u2 = api.create_user(
            email='email2@email2',
            name='name2',
            do_notify=False,
            do_save=True,
        )
        u3 = api.create_user(
            email='notfound@notfound',
            name='notfound',
            do_notify=False,
            do_save=True,
        )
        wapi = WorkspaceApi(
            current_user=admin,
            session=self.session,
            config=self.app_config,
        )
        workspace = wapi.create_workspace(
            'test workspace n°1',
            save_now=True)
        role_api = RoleApi(
            current_user=admin,
            session=self.session,
            config=self.app_config,
        )
        role_api.create_one(u1, workspace, UserRoleInWorkspace.READER, False)
        role_api.create_one(u2, workspace, UserRoleInWorkspace.READER, False)
        role_api.create_one(u3, workspace, UserRoleInWorkspace.READER, False)
        api2 = UserApi(
            current_user=u1,
            session=self.session,
            config=self.config,
        )
        users = api2.get_known_user('email')
        assert len(users) == 2
        assert users[0] == u1
        assert users[1] == u2

    def test_unit__get_known__user__admin__by_name(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u1 = api.create_user(
            email='email@email',
            name='name',
            do_notify=False,
            do_save=True,
        )

        users = api.get_known_user('nam')
        assert len(users) == 1
        assert users[0] == u1

    def test_unit__get_one__ok__nominal_case(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        u = api.create_minimal_user('titi@titi')
        api.update(u, 'titi', 'titi@titi', 'pass', do_save=True)
        one = api.get_one(u.user_id)
        eq_(u.user_id, one.user_id)

    def test_unit__get_user_with_context__nominal_case(self):
        user = User(
            email='admin@tracim.tracim',
            display_name='Admin',
            is_active=True,
        )
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        new_user = api.get_user_with_context(user)
        assert isinstance(new_user, UserInContext)
        assert new_user.user == user
        assert new_user.profile == 'nobody'
        assert new_user.user_id == user.user_id
        assert new_user.email == 'admin@tracim.tracim'
        assert new_user.display_name == 'Admin'
        assert new_user.is_active is True
        # TODO - G.M - 03-05-2018 - [avatar][calendar] Should test this
        # with true value when those param will be available.
        assert new_user.avatar_url is None
        assert new_user.calendar_url is None

    def test_unit__get_current_user_ok__nominal_case(self):
        user = User(email='admin@tracim.tracim')
        api = UserApi(
            current_user=user,
            session=self.session,
            config=self.config,
        )
        new_user = api.get_current_user()
        assert isinstance(new_user, User)
        assert user == new_user

    def test_unit__get_current_user__err__user_not_exist(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        with pytest.raises(UserDoesNotExist):
            api.get_current_user()

    def test_unit__authenticate_user___ok__nominal_case(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        user = api.authenticate_user('admin@admin.admin', 'admin@admin.admin')
        assert isinstance(user, User)
        assert user.email == 'admin@admin.admin'

    def test_unit__authenticate_user___err__user_not_active(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        gapi = GroupApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        groups = [gapi.get_one_with_name('users')]
        user = api.create_user(
            email='test@test.test',
            password='pass',
            name='bob',
            groups=groups,
            timezone='Europe/Paris',
            do_save=True,
            do_notify=False,
        )
        api.disable(user)
        with pytest.raises(UserNotActive):
            api.authenticate_user('test@test.test', 'test@test.test')

    def test_unit__authenticate_user___err__wrong_password(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        with pytest.raises(AuthenticationFailed):
            api.authenticate_user('admin@admin.admin', 'wrong_password')

    def test_unit__authenticate_user___err__wrong_user(self):
        api = UserApi(
            current_user=None,
            session=self.session,
            config=self.config,
        )
        with pytest.raises(AuthenticationFailed):
            api.authenticate_user('admin@admin.admin', 'wrong_password')
