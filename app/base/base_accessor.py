import typing
from logging import getLogger
from sqlalchemy.engine import ChunkedIteratorResult

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BaseAccessor:
    def __init__(self, app: "Application", *args, **kwargs):
        self.app = app
        self.logger = getLogger("accessor")
        app.on_startup.append(self.connect)
        app.on_cleanup.append(self.disconnect)

    async def connect(self, app: "Application"):
        return

    async def disconnect(self, app: "Application"):
        return

    async def make_get_query(self, query):
        async with self.app.database.session() as session:
            result: ChunkedIteratorResult = await session.execute(query)
            return result

    async def make_add_query(self, new_object):
        async with self.app.database.session() as session:
            session.add(new_object)
            await session.commit()

    async def make_update_query(self, update_query):
        async with self.app.database.session() as session:
            result: ChunkedIteratorResult = await session.execute(update_query)
            await session.commit()
            return result
