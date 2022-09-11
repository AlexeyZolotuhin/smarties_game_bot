from aiohttp_apispec import docs, response_schema, request_schema

from app.admin.models import Admin
from app.admin.schemes import AdminSchema, RequestAdminSchema, ResponseAdminSchema
from app.web.app import View
from aiohttp.web_exceptions import HTTPForbidden
from aiohttp_session import new_session

from app.web.decorators import require_auth
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=["Smarties game bot"], summary="AdminLoginView", description="Login admin-user in app")
    @request_schema(RequestAdminSchema)
    @response_schema(ResponseAdminSchema, 200)
    async def post(self):
        data = self.request["data"]
        admin: Admin = await self.store.admins.get_by_login(data["login"])
        if admin is None or not admin.is_password_valid(data["password"]):
            raise HTTPForbidden(text='{"admin": ["Wrong admin login or password."]}')

        session = await new_session(request=self.request)
        admin_json = AdminSchema().dump(admin)
        session["admin"] = admin_json

        return json_response(data=admin_json)


class AdminCurrentView(View):
    @docs(tags=["Smarties game bot"], summary="AdminCurrentView", description="Get current admin")
    @response_schema(ResponseAdminSchema, 200)
    @require_auth
    async def get(self):
        admin = self.request.admin
        return json_response(data=AdminSchema().dump(admin))
