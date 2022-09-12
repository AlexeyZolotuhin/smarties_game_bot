import typing
from app.game.views import PathwayAddView, PathwayListView, GamerAddView, GamerListView, UpdateGamerVictoriesView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    # app.router.add_view("/game.add_pathway", PathwayAddView)
    # app.router.add_view("/game.list_pathway", PathwayListView)
    app.router.add_view("/game.add_gamer", GamerAddView)
    app.router.add_view("/game.list_gamers", GamerListView)
    app.router.add_view("/game.update_victories_gamer", UpdateGamerVictoriesView)
