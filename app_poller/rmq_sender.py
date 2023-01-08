from dataclasses import dataclass
from aio_pika import connect, Message, ExchangeType, DeliveryMode
import json


@dataclass
class RmqSenderConfig:
    rabbit_url: str
    queue_name: str
    token: str


class RmqSender:
    def __init__(self, config: RmqSenderConfig):
        self.config = config
        self.connection = None

    async def __aenter__(self):
        self.connection = await connect(self.config.rabbit_url)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def put(self, data: dict):
        if self.connection is None:
            self.connection = await connect(self.config.rabbit_url)

        channel = await self.connection.channel()
        bot_exchange = await channel.declare_exchange(
            "bot_exchange", ExchangeType.DIRECT
        )
        queue = await channel.declare_queue(name=self.config.queue_name,
                                            durable=True)
        await queue.bind(bot_exchange, routing_key=self.config.queue_name)
        await bot_exchange.publish(
            Message((json.dumps(data)).encode(),
                    delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=self.config.queue_name,
        )

    async def start(self):
        if self.connection is None:
            try:
                self.connection = await connect(self.config.rabbit_url)
            except Exception as e:
                print(f"Wrong connection {e}")

    async def stop(self):
        if self.connection:
            await self.connection.close()
