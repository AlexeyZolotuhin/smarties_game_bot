import typing
from sqlite3 import IntegrityError

from sqlalchemy import select

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

# from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):

    async def connect(self, app: "Application"):
        self.app = app
        try:
            admin = await self.create_admin(self.app.config.admin.login, self.app.config.admin.password)
            print(f"created admin user in DB: {admin.login}")
        except IntegrityError as e:
            pass
            # match e.orig.pgcode:
            #     case '23505':
            #         raise HTTPConflict
        except Exception:
            pass

    async def get_by_login(self, login: str) -> Admin | None:
        query = select(AdminModel).where(AdminModel.login == login)
        res = await self.make_get_query(query)
        admin = None
        result = res.scalars().first()
        if result:
            admin = Admin(id=result.id, login=result.login, password=result.password)
        return admin

    async def create_admin(self, login: str, password: str) -> Admin:
        new_admin = AdminModel()
        new_admin.set_attr(login=login, password=password)
        await self.make_add_query(new_admin)
        return Admin(id=new_admin.id, login=new_admin.login)
