from typing import Optional
from dataclasses import dataclass
from app.store.database import db
from datetime import datetime, timedelta
from sqlalchemy.orm import relation
from sqlalchemy import (
    Column,
    Integer,
    VARCHAR,
    ForeignKey,
    BOOLEAN,
    DateTime
)

# model was replaced by config file (app.config.game.difficulty_levels)
# @dataclass
# class Pathway:
#     id: int
#     color: str
#     max_questions: int
#     max_mistakes: int


@dataclass
class Gamer:
    id: int
    id_tguser: int
    username: str
    number_of_defeats: int
    number_of_victories: int


@dataclass
class GameSession:
    id: int
    chat_id: int
    game_start: datetime
    game_end: datetime
    state: str  # Active, Ended, Interrupted
    theme_id: int  # -1 - without theme
    time_for_game: int  # in minutes
    time_for_answer: int  # in seconds
    game_progress: Optional[list["GameProgress"]] = None


@dataclass
class GameProgress:
    id: int
    id_gamer: int
    difficulty_level: int
    gamer_status: str  # Playing, Winner, Failed
    number_of_mistakes: int
    number_of_right_answers: int
    is_master: int
    id_gamesession: int

# model was replaced by config file (app.config.game.difficulty_levels)
# class PathwayModel(db):
#     __tablename__ = "pathways"
#     id = Column(Integer, primary_key=True)
#     color = Column(VARCHAR(20), nullable=False, unique=True)
#     max_questions = Column(Integer, nullable=False)
#     max_mistakes = Column(Integer, nullable=False)
#     game_progress = relation("GameProgressModel", back_populates="pathway")
#
#     def __repr__(self):
#         return f"<Pathway(id='{self.id}', color='{self.color}')>"
#
#     def to_pathway_dataclass(self) -> Pathway:
#         return Pathway(
#             id=self.id,
#             color=self.color,
#             max_questions=self.max_questions,
#             max_mistakes=self.max_mistakes,
#         )


class GamerModel(db):
    __tablename__ = "gamers"
    id = Column(Integer, primary_key=True)
    id_tguser = Column(Integer, nullable=False, unique=True)
    username = Column(VARCHAR(50), nullable=False)
    number_of_defeats = Column(Integer, default=0, nullable=False)
    number_of_victories = Column(Integer, default=0, nullable=False)
    game_progress = relation("GameProgressModel", back_populates="gamer")

    def __repr__(self):
        return f"<Gamer(id='{self.id}', id_tguser='{self.id_tguser}', username='{self.username}')>"


class GameSessionModel(db):
    __tablename__ = "game_sessions"
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    game_start = Column(DateTime, default=datetime.utcnow)
    game_end = Column(DateTime)
    state = Column(VARCHAR(15), default='Active')  # Active, Ended, Interrupted
    theme_id = Column(Integer, default=-1)  # -1 without theme, random any question
    time_for_game = Column(Integer, default=5)  # in minutes
    time_for_answer = Column(Integer, default=15)  # in seconds
    game_progress = relation("GameProgressModel", back_populates="game_session")

    def __repr__(self):
        return f"<GameSession(id='{self.id}', chat_id='{self.chat_id}', state='{self.state}')>"


class GameProgressModel(db):
    __tablename__ = "game_progress"
    id = Column(Integer, primary_key=True)
    id_gamer = Column(Integer, ForeignKey("gamers.id", ondelete="CASCADE"), nullable=False)
    difficulty_level = Column(Integer, nullable=False)
    is_master = Column(BOOLEAN, default=False)
    id_gamesession = Column(Integer, ForeignKey("game_sessions.id", ondelete="CASCADE",
                                                onupdate="CASCADE"), nullable=False)
    gamer_status = Column(VARCHAR(15), default="Playing")  # Playing, Winner, Failed
    number_of_mistakes = Column(Integer, default=0)
    number_of_right_answers = Column(Integer, default=0)

    gamer = relation("GamerModel", back_populates="game_progress")
    game_session = relation("GameSessionModel", back_populates="game_progress")

    def __repr__(self):
        return f"<GameProgressModel(id='{self.id}', id_gamer='{self.id_gamer}', gamer_status='{self.gamer_status}')>"
