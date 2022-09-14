import typing
from app.game.views import PathwayAddView, PathwayListView, GamerAddView, GamerListView, UpdateGamerVictoriesView, \
    UpdateGamerDefeatsView, GameSessionAddView, UpdateGameSessionTimeoutView, GameSessionListView, \
    GameSessionByChatIdView, GameProgressAddView, GameProgressListView, AllGameInfoView

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    # app.router.add_view("/game.add_pathway", PathwayAddView)
    # app.router.add_view("/game.list_pathway", PathwayListView)
    app.router.add_view("/game.add_gamer", GamerAddView)
    app.router.add_view("/game.list_gamers", GamerListView)
    app.router.add_view("/game.update_victories_gamer", UpdateGamerVictoriesView)
    app.router.add_view("/game.update_defeats_gamer", UpdateGamerDefeatsView)
    app.router.add_view("/game.add_game_session", GameSessionAddView)
    app.router.add_view("/game.update_timeout_gs", UpdateGameSessionTimeoutView)
    app.router.add_view("/game.list_gs", GameSessionListView)
    app.router.add_view("/game.get_gs_by_chatid", GameSessionByChatIdView)
    app.router.add_view("/game.add_gp", GameProgressAddView)
    app.router.add_view("/game.list_gp", GameProgressListView)
    app.router.add_view("/game.all_game_info", AllGameInfoView)
