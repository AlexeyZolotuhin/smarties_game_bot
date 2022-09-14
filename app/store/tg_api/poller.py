import asyncio
from asyncio import Task
from typing import Optional
from aiohttp import ClientOSError
from app.store.tg_api.api import TgClient


class Poller:
    def __init__(self, token: str, queue: asyncio.Queue):
        self.tg_client = TgClient(token)
        self.queue = queue
        self._task: Optional[Task] = None
        self.is_running = False

    async def poll(self):
        offset = 0
        while self.is_running:
            try:
                res = await self.tg_client.get_updates_in_objects(offset=offset, timeout=15)
                print(res)
            except ClientOSError:
                continue
            for update in res.result:  # ["result"]:
                offset = update.update_id + 1  #update["update_id"] + 1
                self.queue.put_nowait(update)


    async def start(self):
        self.is_running = True
        self._task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        if self._task:
            await asyncio.wait([self._task], timeout=30)
