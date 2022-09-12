from sqlite3 import IntegrityError
from aiohttp.web_exceptions import HTTPConflict, HTTPInternalServerError

from app.game.schemes import RequestPathwaySchema, PathwaySchema, ResponsePathwaySchema, ResponsePathwayListSchema, \
    PathwayListSchema, RequestGamerSchema, ResponseGamerSchema, GamerSchema, ResponseGamerListSchema, GamerListSchema, \
    UpdateVictoriesGamerSchema
from app.web.app import View
from app.web.decorators import require_auth
from app.web.schema import OkResponseSchema
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
    @response_schema(ResponseGamerSchema)
    async def post(self):
        data = self.request["data"]
        try:
            gamer = await self.store.game.update_gamer_victories(data["id_tguser"], data["number_of_victories"])
        except IntegrityError as e:
            raise HTTPInternalServerError(text='{"gamer": ["something wrong in update victories."]}')

        return json_response(data=GamerSchema().dump(gamer))

# class GameSessionAddView(View):
#     @docs(tags=["Smarties game bot"], summary="GameSessionAddView", description="Add new game session")
#     # @request_schema(RequestPathwaySchema)
#     @response_schema(OkResponseSchema, 200)
#     @require_auth
#     async def post(self):
#         data = self.request["data"]
#         try:
#             game_session = await self.store.game.create_game_session()
#         except IntegrityError as e:
#             match e.orig.pgcode:
#                 case '23505':
#                     raise HTTPConflict(text='{"pathway": ["pathway already exists."]}')
#
#         return json_response(data=PathwaySchema().dump())
