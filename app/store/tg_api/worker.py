import asyncio
import json
from typing import List
from aio_pika import connect, ExchangeType, IncomingMessage
from app.store import Store
from app.store.tg_api.dataclasses import UpdateObj
from app.store.tg_api.dataclasses import RmqReceiverConfig


class Worker:
    def __init__(self, store: Store, config: RmqReceiverConfig, concurrent_workers: int):
        self.config = config
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []
        self.store = store

    async def call_handler(self, msg: IncomingMessage):
        async with msg.process():
            upd_dict = json.loads(msg.body.decode())
            upd = UpdateObj.Schema().load(upd_dict)
            await self.store.bots_manager.handle_update(upd)

    async def _worker(self):
        self.connection = await connect(self.config.rabbit_url)
        channel = await self.connection.channel()
        bot_exchange = await channel.declare_exchange(
            "bot_exchange", ExchangeType.DIRECT
        )
        print("create channel to rabbitmq")
        queue = await channel.declare_queue(self.config.queue_name, durable=True)
        await queue.bind(bot_exchange, routing_key=self.config.queue_name)
        await queue.consume(self.call_handler)

    async def start(self):
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.concurrent_workers)]

    async def stop(self):
        for t in self._tasks:
            t.cancel()

