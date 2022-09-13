from sqlite3 import IntegrityError
from aiohttp.web_exceptions import HTTPConflict, HTTPInternalServerError

from app.game.schemes import RequestPathwaySchema, PathwaySchema, ResponsePathwaySchema, ResponsePathwayListSchema, \
    PathwayListSchema, RequestGamerSchema, ResponseGamerSchema, GamerSchema, ResponseGamerListSchema, GamerListSchema, \
    UpdateVictoriesGamerSchema, UpdateDefeatsGamerSchema, RequestChatIdSchema, ResponseGameSessionSchema, \
    GameSessionSchema, RequestTimeOutSchema, ResponseGameSessionListSchema, GameSessionListSchema, \
    RequestGameProgressSchema, ResponseGameProgressSchema, GameProgressSchema
from app.web.app import View
from app.web.decorators import require_auth
from app.web.utils import json_response
from aiohttp_apispec import docs, response_schema, request_schema
from sqlalchemy.exc import IntegrityError


class PathwayAddView(View):
    @docs(tags=["Smarties game bot"], summary="PathwayAddView", description="Add new pathway (difficulty level)")
    @request_schema(RequestPathwaySchema)
    @response_schema(ResponsePathwaySchema, 200)
    @require_auth
    async def post(self):
        data = self.request["data"]
        try:
            pathway = await self.store.game.create_pathway(color=data["color"],
                                                           max_questions=data["max_questions"],
                                                           max_mistakes=data["max_mistakes"], )
        except IntegrityError as e:
            match e.orig.pgcode:
                case '23505':
                    raise HTTPConflict(text='{"pathway": ["pathway already exists."]}')

        return json_response(data=PathwaySchema().dump(pathway))


class PathwayListView(View):
    @docs(tags=["Smarties game bot"], summary="PathwayListView", description="Get list of all pathways")
    @response_schema(ResponsePathwayListSchema, 200)
    @require_auth
    async def get(self):
        pathways = await self.store.game.list_pathways()
        return json_response(data=PathwayListSchema().dump({"pathways": pathways}))


class GamerAddView(View):
    @docs(tags=["Smarties game bot"], summary="GamerAddView", description="Add new gamer")
    @request_schema(RequestGamerSchema)
    @response_schema(ResponseGamerSchema)
    @require_auth
    async def post(self):
        data = self.request["data"]
        try:
            gamer = await self.store.game.create_gamer(data["id_tguser"], data["username"])
        except IntegrityError as e:
            match e.orig.pgcode:
                case '23505':
                    raise HTTPConflict(text='{"gamer": ["gamer already exists."]}')

        return json_response(data=GamerSchema().dump(gamer))


class GamerListView(View):
    @docs(tags=["Smarties game bot"], summary="GamerListView", description="Get list all gamers")
    @response_schema(ResponseGamerListSchema)
    @require_auth
    async def get(self):
        gamers = await self.store.game.list_gamers()
        return json_response(data=GamerListSchema().dump({"gamers": gamers}))


class UpdateGamerVictoriesView(View):
    @docs(tags=["Smarties game bot"], summary="UpdateGamerVictoriesView",
          description="Set number of gamer's victories.")
    @request_schema(UpdateVictoriesGamerSchema)
    @response_schema(ResponseGamerSchema, 200)
    async def post(self):
        data = self.request["data"]
        try:
            gamer = await self.store.game.update_gamer_victories(data["id_tguser"], data["number_of_victories"])
        except IntegrityError as e:
            raise HTTPInternalServerError(text='{"gamer": ["something wrong in update victories."]}')

        return json_response(data=GamerSchema().dump(gamer))


class UpdateGamerDefeatsView(View):
    @docs(tags=["Smarties game bot"], summary="UpdateGamerVictoriesView",
          description="Set number of gamer's victories.")
    @request_schema(UpdateDefeatsGamerSchema)
    @response_schema(ResponseGamerSchema, 200)
    async def post(self):
        data = self.request["data"]
        try:
            gamer = await self.store.game.update_gamer_defeats(data["id_tguser"], data["number_of_defeats"])
        except IntegrityError as e:
            raise HTTPInternalServerError(text='{"gamer": ["something wrong in update defeats."]}')

        return json_response(data=GamerSchema().dump(gamer))


class GameSessionAddView(View):
    @docs(tags=["Smarties game bot"], summary="GameSessionAddView", description="Add new game session")
    @request_schema(RequestChatIdSchema)
    @response_schema(ResponseGameSessionSchema, 200)
    @require_auth
    async def post(self):
        data = self.request["data"]
        try:
            game_session = await self.store.game.create_game_session(data["chat_id"])
        except IntegrityError as e:
            match e.orig.pgcode:
                case '23505':
                    raise HTTPConflict(text='{"game_session": ["already exists."]}')

        return json_response(data=GameSessionSchema().dump(game_session))


class GameSessionListView(View):
    @docs(tags=["Smarties game bot"], summary="GameSessionListView", description="Get list all game sessions")
    @response_schema(ResponseGameSessionListSchema)
    @require_auth
    async def get(self):
        game_sessions = await self.store.game.list_game_sessions()
        print(game_sessions)
        return json_response(data=GameSessionListSchema().dump({"game_sessions": game_sessions}))


class GameSessionByChatIdView(View):
    @docs(tags=["Smarties game bot"], summary="GameSessionByChatIdView", description="Get active GS by chat_id")
    @response_schema(ResponseGameSessionListSchema)
    @require_auth
    async def get(self):
        data = await self.request.json()
        game_session = await self.store.game.get_gs_by_chat_id(chat_id=data["chat_id"])
        return json_response(data=GameSessionSchema().dump(game_session))


class UpdateGameSessionTimeoutView(View):
    @docs(tags=["Smarties game bot"], summary="UpdateGameSessionTimeoutView",
          description="Change time for answer in game session")
    @request_schema(RequestTimeOutSchema)
    @response_schema(ResponseGameSessionSchema, 200)
    @require_auth
    async def post(self):
        data = self.request["data"]
        try:
            game_session = await self.store.game.update_gs_timeout(data["chat_id"], data["time_for_answer"])
        except IntegrityError as e:
            raise HTTPInternalServerError(text='{"game_session": ["something wrong in update timeout."]}')

        return json_response(data=GameSessionSchema().dump(game_session))


class GameProgressAddView(View):
    @docs(tags=["Smarties game bot"], summary="GameProgressAddView", description="Add new game progress")
    @request_schema(RequestGameProgressSchema)
    @response_schema(ResponseGameProgressSchema, 200)
    @require_auth
    async def post(self):
        data = self.request["data"]
        try:
            game_progress = await self.store.game.create_game_progress(data["id_gamer"], data["id_gamesession"])
        except IntegrityError as e:
            match e.orig.pgcode:
                case '23505':
                    raise HTTPConflict(text='{"game_progress": ["already exists."]}')

        return json_response(data=GameProgressSchema().dump(game_progress))
