from typing import Optional, TYPE_CHECKING
from app.base.base_accessor import BaseAccessor
from app.store.tg_api.worker import Worker
from app.store.tg_api.dataclasses import RmqReceiverConfig

if TYPE_CHECKING:
    from app.web.app import Application


class TgApiAccessor(BaseAccessor):
    def __init__(self, app: "Aplication", number_workers: int, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.worker: Optional[Worker] = None
        self.number_workers = number_workers

    async def connect(self, app: "Application"):

        rmq_config_receiver = RmqReceiverConfig(
            queue_name="smart_bot",
            rabbit_url="amqp://user_mq:pass_mq@tg-rabbitmq:5672/",
            capacity=1,
        )

        self.worker = Worker(self.app.store, rmq_config_receiver, self.number_workers)
        await self.worker.start()

    async def disconnect(self, app: "Application"):
        if self.worker:
            await self.worker.stop()
