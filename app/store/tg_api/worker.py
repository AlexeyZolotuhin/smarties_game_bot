import asyncio
import datetime
from typing import List

from app.store import Store


class Worker:
    def __init__(self, store: Store, token: str, queue: asyncio.Queue, concurrent_workers: int):
        self.queue = queue
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []
        self.store = store

    async def _worker(self):
        while True:
            upd = await self.queue.get()
            try:
                await self.store.bots_manager.handle_update(upd)
            finally:
                self.queue.task_done()

    async def start(self):
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.concurrent_workers)]

    async def stop(self):
        await self.queue.join()
        for t in self._tasks:
            t.cancel()
