from sqlite3 import IntegrityError
from aiohttp.web_exceptions import HTTPConflict

from app.game.schemes import RequestPathwaySchema, PathwaySchema, ResponsePathwaySchema, ResponsePathwayListSchema, \
    PathwayListSchema
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
