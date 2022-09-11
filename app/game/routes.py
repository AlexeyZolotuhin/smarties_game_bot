import typing
from app.game.views import PathwayAddView, PathwayListView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    app.router.add_view("/game.add_pathway", PathwayAddView)
    app.router.add_view("/game.list_pathway", PathwayListView)
