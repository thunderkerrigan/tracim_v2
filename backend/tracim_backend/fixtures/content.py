# -*- coding: utf-8 -*-
from depot.io.utils import FileIntent
import transaction

from tracim_backend import models
from tracim_backend.fixtures import Fixture
from tracim_backend.fixtures.users_and_groups import Test
from tracim_backend.lib.core.content import ContentApi
from tracim_backend.lib.core.userworkspace import RoleApi
from tracim_backend.lib.core.workspace import WorkspaceApi
from tracim_backend.models.contents import CONTENT_TYPES
from tracim_backend.models.data import UserRoleInWorkspace
from tracim_backend.models.revision_protection import new_revision


class Content(Fixture):
    require = [Test]

    def insert(self):
        admin = self._session.query(models.User) \
            .filter(models.User.email == 'admin@admin.admin') \
            .one()
        bob = self._session.query(models.User) \
            .filter(models.User.email == 'bob@fsf.local') \
            .one()
        john_the_reader = self._session.query(models.User) \
            .filter(models.User.email == 'john-the-reader@reader.local') \
            .one()

        admin_workspace_api = WorkspaceApi(
            current_user=admin,
            session=self._session,
            config=self._config,
        )
        bob_workspace_api = WorkspaceApi(
            current_user=bob,
            session=self._session,
            config=self._config
        )
        content_api = ContentApi(
            current_user=admin,
            session=self._session,
            config=self._config
        )
        bob_content_api = ContentApi(
            current_user=bob,
            session=self._session,
            config=self._config
        )
        reader_content_api = ContentApi(
            current_user=john_the_reader,
            session=self._session,
            config=self._config
        )
        role_api = RoleApi(
            current_user=admin,
            session=self._session,
            config=self._config,
        )

        # Workspaces
        business_workspace = admin_workspace_api.create_workspace(
            'Business',
            description='All importants documents',
            save_now=True,
        )
        recipe_workspace = admin_workspace_api.create_workspace(
            'Recipes',
            description='Our best recipes',
            save_now=True,
        )
        other_workspace = bob_workspace_api.create_workspace(
            'Others',
            description='Other Workspace',
            save_now=True,
        )

        # Workspaces roles
        role_api.create_one(
            user=bob,
            workspace=recipe_workspace,
            role_level=UserRoleInWorkspace.CONTENT_MANAGER,
            with_notif=False,
        )
        role_api.create_one(
            user=john_the_reader,
            workspace=recipe_workspace,
            role_level=UserRoleInWorkspace.READER,
            with_notif=False,
        )
        # Folders

        tool_workspace = content_api.create(
            content_type_slug=CONTENT_TYPES.Folder.slug,
            workspace=business_workspace,
            label='Tools',
            do_save=True,
            do_notify=False,
        )
        menu_workspace = content_api.create(
            content_type_slug=CONTENT_TYPES.Folder.slug,
            workspace=business_workspace,
            label='Menus',
            do_save=True,
            do_notify=False,
        )

        dessert_folder = content_api.create(
            content_type_slug=CONTENT_TYPES.Folder.slug,
            workspace=recipe_workspace,
            label='Desserts',
            do_save=True,
            do_notify=False,
        )
        salads_folder = content_api.create(
            content_type_slug=CONTENT_TYPES.Folder.slug,
            workspace=recipe_workspace,
            label='Salads',
            do_save=True,
            do_notify=False,
        )
        other_folder = content_api.create(
            content_type_slug=CONTENT_TYPES.Folder.slug,
            workspace=other_workspace,
            label='Infos',
            do_save=True,
            do_notify=False,
        )

        # Pages, threads, ..
        tiramisu_page = content_api.create(
            content_type_slug=CONTENT_TYPES.Page.slug,
            workspace=recipe_workspace,
            parent=dessert_folder,
            label='Tiramisu Recipes!!!',
            do_save=True,
            do_notify=False,
        )
        with new_revision(
                session=self._session,
                tm=transaction.manager,
                content=tiramisu_page,
        ):
            content_api.update_content(
                item=tiramisu_page,
                new_content='<p>To cook a greet Tiramisu, you need many ingredients.</p>',  # nopep8
                new_label='Tiramisu Recipes!!!',
            )
            content_api.save(tiramisu_page)

        best_cake_thread = content_api.create(
            content_type_slug=CONTENT_TYPES.Thread.slug,
            workspace=recipe_workspace,
            parent=dessert_folder,
            label='Best Cake',
            do_save=False,
            do_notify=False,
        )
        best_cake_thread.description = 'Which is the best cake?'
        self._session.add(best_cake_thread)
        apple_pie_recipe = content_api.create(
            content_type_slug=CONTENT_TYPES.File.slug,
            workspace=recipe_workspace,
            parent=dessert_folder,
            label='Apple_Pie',
            do_save=False,
            do_notify=False,
        )
        apple_pie_recipe.file_extension = '.txt'
        apple_pie_recipe.depot_file = FileIntent(
            b'Apple pie Recipe',
            'apple_Pie.txt',
            'text/plain',
        )
        self._session.add(apple_pie_recipe)
        Brownie_recipe = content_api.create(
            content_type_slug=CONTENT_TYPES.File.slug,
            workspace=recipe_workspace,
            parent=dessert_folder,
            label='Brownie Recipe',
            do_save=False,
            do_notify=False,
        )
        Brownie_recipe.file_extension = '.html'
        Brownie_recipe.depot_file = FileIntent(
            b'<p>Brownie Recipe</p>',
            'brownie_recipe.html',
            'text/html',
        )
        self._session.add(Brownie_recipe)
        fruits_desserts_folder = content_api.create(
            content_type_slug=CONTENT_TYPES.Folder.slug,
            workspace=recipe_workspace,
            label='Fruits Desserts',
            parent=dessert_folder,
            do_save=True,
        )

        menu_page = content_api.create(
            content_type_slug=CONTENT_TYPES.Page.slug,
            workspace=business_workspace,
            parent=menu_workspace,
            label='Current Menu',
            do_save=True,
        )

        new_fruit_salad = content_api.create(
            content_type_slug=CONTENT_TYPES.Page.slug,
            workspace=recipe_workspace,
            parent=fruits_desserts_folder,
            label='New Fruit Salad',
            do_save=True,
        )
        old_fruit_salad = content_api.create(
            content_type_slug=CONTENT_TYPES.Page.slug,
            workspace=recipe_workspace,
            parent=fruits_desserts_folder,
            label='Fruit Salad',
            do_save=True,
            do_notify=False,
        )
        with new_revision(
                session=self._session,
                tm=transaction.manager,
                content=old_fruit_salad,
        ):
            content_api.archive(old_fruit_salad)
        content_api.save(old_fruit_salad)

        bad_fruit_salad = content_api.create(
            content_type_slug=CONTENT_TYPES.Page.slug,
            workspace=recipe_workspace,
            parent=fruits_desserts_folder,
            label='Bad Fruit Salad',
            do_save=True,
            do_notify=False,
        )
        with new_revision(
                session=self._session,
                tm=transaction.manager,
                content=bad_fruit_salad,
        ):
            content_api.delete(bad_fruit_salad)
        content_api.save(bad_fruit_salad)

        # File at the root for test
        new_fruit_salad = content_api.create(
            content_type_slug=CONTENT_TYPES.Page.slug,
            workspace=other_workspace,
            label='New Fruit Salad',
            do_save=True,
        )
        old_fruit_salad = content_api.create(
            content_type_slug=CONTENT_TYPES.Page.slug,
            workspace=other_workspace,
            label='Fruit Salad',
            do_save=True,
        )
        with new_revision(
                session=self._session,
                tm=transaction.manager,
                content=old_fruit_salad,
        ):
            content_api.archive(old_fruit_salad)
        content_api.save(old_fruit_salad)

        bad_fruit_salad = content_api.create(
            content_type_slug=CONTENT_TYPES.Page.slug,
            workspace=other_workspace,
            label='Bad Fruit Salad',
            do_save=True,
        )
        with new_revision(
                session=self._session,
                tm=transaction.manager,
                content=bad_fruit_salad,
        ):
            content_api.delete(bad_fruit_salad)
        content_api.save(bad_fruit_salad)

        content_api.create_comment(
            parent=best_cake_thread,
            content='<p>What is for you the best cake ever? </br> I personnally vote for Chocolate cupcake!</p>',  # nopep8
            do_save=True,
        )
        bob_content_api.create_comment(
            parent=best_cake_thread,
            content='<p>What about Apple Pie? There are Awesome!</p>',
            do_save=True,
        )
        reader_content_api.create_comment(
            parent=best_cake_thread,
            content='<p>You are right, but Kouign-amann are clearly better.</p>',
            do_save=True,
        )
        with new_revision(
                session=self._session,
                tm=transaction.manager,
                content=best_cake_thread,
        ):
            bob_content_api.update_content(
                item=best_cake_thread,
                new_content='What is the best cake?',
                new_label='Best Cakes?',
            )
            bob_content_api.save(best_cake_thread)

        with new_revision(
                session=self._session,
                tm=transaction.manager,
                content=tiramisu_page,
        ):
            bob_content_api.update_content(
                item=tiramisu_page,
                new_content='<p>To cook a great Tiramisu, you need many ingredients.</p>',  # nopep8
                new_label='Tiramisu Recipe',
            )
            bob_content_api.save(tiramisu_page)
        self._session.flush()
