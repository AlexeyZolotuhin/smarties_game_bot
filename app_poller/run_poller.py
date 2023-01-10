import asyncio
from typing import Optional
from app_poller.poller import Poller
from app_poller.rmq_sender import RmqSenderConfig
import os
import yaml


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


def get_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "configs/config.yml")
    print(config_path)

    with open(config_path, "r", encoding="utf8") as f:
        raw_config = yaml.safe_load(f)

    return {"queue_name": raw_config["rabbitmq"]["queue_name"],
            "rabbit_url": raw_config["rabbitmq"]["rabbit_url"],
            "bot_token": raw_config["bot"]["token"]}


def run_poller():
    config = get_config()

    rmq_config_sender = RmqSenderConfig(
        queue_name=config["queue_name"],
        rabbit_url=config["rabbit_url"],
        token=config["bot_token"]
    )

    bot_poller = BotPoller(rmq_config_sender)
    loop = asyncio.get_event_loop()
    loop.create_task(bot_poller.connect())
    loop.run_forever()
