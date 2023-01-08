import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    login: str
    password: str


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"


@dataclass
class DifficultyLevel:
    color: str
    max_questions: int
    max_mistakes: int


@dataclass
class GameConfig:
    theme_id: int
    time_for_game: int
    time_for_answer: int
    difficulty_levels: dict["DifficultyLevel"]


@dataclass
class BotConfig:
    access_token: str
    id: int


@dataclass
class RabbitConfig:
    queue_name: str
    rabbit_url: str


@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig = None
    database: DatabaseConfig = None
    game: GameConfig = None
    bot: BotConfig = None
    rabbit: RabbitConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r", encoding="utf8") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        session=SessionConfig(
            key=raw_config["session"]["key"],
        ),
        admin=AdminConfig(
            login=raw_config["admin"]["login"],
            password=raw_config["admin"]["password"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
        bot=BotConfig(
            access_token=raw_config["bot"]["token"],
            id=raw_config["bot"]["id"]
        ),
        game=GameConfig(
            theme_id=raw_config["game"]["theme_id"],
            time_for_game=raw_config["game"]["time_for_game"],
            time_for_answer=raw_config["game"]["time_for_answer"],
            difficulty_levels={dl_k: DifficultyLevel(color=dl_v["color"],
                                                     max_questions=dl_v["max_questions"],
                                                     max_mistakes=dl_v["max_mistakes"]
                                                     ) for dl_k, dl_v in raw_config["game"]["difficulty_levels"].items()
                               }
        ),
        rabbit=RabbitConfig(
            queue_name=raw_config["rabbitmq"]["queue_name"],
            rabbit_url=raw_config["rabbitmq"]["rabbit_url"],
        ),
    )
