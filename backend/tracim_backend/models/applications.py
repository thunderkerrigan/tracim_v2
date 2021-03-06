# coding=utf-8
import typing


class Application(object):
    """
    Application class with data needed for frontend
    """
    def __init__(
            self,
            label: str,
            slug: str,
            fa_icon: str,
            hexcolor: str,
            is_active: bool,
            config: typing.Dict[str, str],
            main_route: str,
    ) -> None:
        """
        @param label: public label of application
        @param slug: identifier of application
        @param icon: font awesome icon class
        @param hexcolor: hexa color of application main color
        @param is_active: True if application enable, False if inactive
        @param config: a dict with eventual application config
        @param main_route: the route of the frontend "home" screen of
        the application. For exemple, if you have an application
        called "calendar", the main route will be something
        like /#/workspace/{wid}/calendar.
        """
        self.label = label
        self.slug = slug
        self.fa_icon = fa_icon
        self.hexcolor = hexcolor
        self.is_active = is_active
        self.config = config
        self.main_route = main_route

    # TODO - G.M - 2018-08-07 - Refactor slug coherence issue like this one.
    # we probably should not have 2 kind of slug
    @property
    def minislug(self):
        return self.slug.replace('contents/', '')


# default apps
calendar = Application(
    label='Calendar',
    slug='calendar',
    fa_icon='calendar',
    hexcolor='#757575',
    is_active=True,
    config={},
    main_route='/#/workspaces/{workspace_id}/calendar',
)

thread = Application(
    label='Threads',
    slug='contents/thread',
    fa_icon='comments-o',
    hexcolor='#ad4cf9',
    is_active=True,
    config={},
    main_route='/#/workspaces/{workspace_id}/contents?type=thread',

)

folder = Application(
    label='Folder',
    slug='contents/folder',
    fa_icon='folder-open-o',
    hexcolor='#252525',
    is_active=True,
    config={},
    main_route='',
)

_file = Application(
    label='Files',
    slug='contents/file',
    fa_icon='paperclip',
    hexcolor='#FF9900',
    is_active=True,
    config={},
    main_route='/#/workspaces/{workspace_id}/contents?type=file',
)

markdownpluspage = Application(
    label='Markdown Plus Documents',  # TODO - G.M - 24-05-2018 - Check label
    slug='contents/markdownpluspage',
    fa_icon='file-code-o',
    hexcolor='#f12d2d',
    is_active=True,
    config={},
    main_route='/#/workspaces/{workspace_id}/contents?type=markdownpluspage',
)

html_documents = Application(
    label='Text Documents',  # TODO - G.M - 24-05-2018 - Check label
    slug='contents/html-document',
    fa_icon='file-text-o',
    hexcolor='#3f52e3',
    is_active=True,
    config={},
    main_route='/#/workspaces/{workspace_id}/contents?type=html-document',
)
# TODO - G.M - 08-06-2018 - This is hardcoded lists of app, make this dynamic.
# List of applications
applications = [
    html_documents,
    # TODO - G.M - 2018-08-02 - Restore markdownpage app
    # markdownpluspage,
    _file,
    thread,
    folder,
    # calendar,
]
