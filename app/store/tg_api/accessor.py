import asyncio, typing
from asyncio import Queue
from typing import Optional
from app.base.base_accessor import BaseAccessor
from app.store.tg_api.poller import Poller
from app.store.tg_api.worker import Worker

if typing.TYPE_CHECKING:
    from app.web.app import Application


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Aplication", number_workers: int, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.queue: Optional[Queue] = None
        self.poller: Optional[Poller] = None
        self.worker: Optional[Worker] = None
        self.number_workers = number_workers

    async def connect(self, app: "Application"):
        token = app.config.bot.access_token
        self.queue = asyncio.Queue()
        self.poller = Poller(token, self.queue)
        self.worker = Worker(self.app.store, token, self.queue, self.number_workers)
        await self.poller.start()
        await self.worker.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.worker:
            await self.worker.stop()
