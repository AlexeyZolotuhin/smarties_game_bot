from typing import Optional, TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine.url import URL
from app.store.database import db

if TYPE_CHECKING:
    from app.web.app import Application


class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        # url = get_url_from_dbconf(self.app.config.database)
        url = URL.create (
            drivername="postgresql+asyncpg",
            host=self.app.config.database.host,
            database=self.app.config.database.database,
            username=self.app.config.database.user,
            password=self.app.config.database.password,
            port=self.app.config.database.port,
        )
        self._engine = create_async_engine(url, echo=True, future=True)
        self.session = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)

    async def disconnect(self, *_: list, **__: dict) -> None:
        try:
            await self._engine.dispose()
        except Exception:
            pass
