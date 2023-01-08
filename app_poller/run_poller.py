import asyncio
from typing import Optional
from app_poller.poller import Poller
from app_poller.rmq_sender import RmqSenderConfig
import os


class BotPoller:
    def __init__(self, config: RmqSenderConfig):
        self.poller: Optional[Poller] = None
        self.config = config

    async def connect(self):
        self.poller = Poller(self.config)
        await self.poller.start()

    async def disconnect(self):
        if self.poller:
            await self.poller.stop()


def run_poller():
    rmq_config_sender = RmqSenderConfig(
        queue_name=os.getenv("QUEUE_NAME"),
        rabbit_url=os.getenv("RABBIT_URL"),
        token=os.getenv("BOT_TOKEN")
    )

    bot_poller = BotPoller(rmq_config_sender)
    loop = asyncio.get_event_loop()
    loop.create_task(bot_poller.connect())
    loop.run_forever()



