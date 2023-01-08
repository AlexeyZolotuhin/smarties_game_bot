import asyncio
from asyncio import Task
from typing import Optional
from aiohttp import ClientOSError
from app_poller.tg_api.tg_client import TgClient
from app_poller.rmq_sender import RmqSender, RmqSenderConfig
from dataclasses import asdict


class Poller:
    def __init__(self, rmq_config: RmqSenderConfig):
        self.tg_client = TgClient(rmq_config.token)
        self.rmq_sender = RmqSender(config=rmq_config)
        self._task: Optional[Task] = None
        self.is_running = False

    async def poll(self):
        offset = 0
        while self.is_running:
            try:
                res = await self.tg_client.get_updates_in_objects(offset=offset, timeout=15)
            except ClientOSError:
                continue
            except Exception as e:
                print(e)

            for update in res.result:  # ["result"]:
                offset = update.update_id + 1  # ["update_id"] + 1
                upd_dict = asdict(update)
                print(upd_dict)
                await self.rmq_sender.put(data=upd_dict)

    async def start(self):
        self.is_running = True
        await self.rmq_sender.start()
        self._task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        if self._task:
            await asyncio.wait([self._task], timeout=30)
        await self.rmq_sender.stop()
