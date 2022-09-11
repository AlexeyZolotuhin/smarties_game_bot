from dataclasses import dataclass
from app.store.database.sqlalchemy_base import db
from sqlalchemy.orm import relation
from sqlalchemy import (
    Column,
    BigInteger,
    VARCHAR,
    ForeignKey,
    BOOLEAN,
)


@dataclass
class Theme:
    id: int
    title: str


@dataclass
class Question:
    id: int
    title: str
    theme_id: int
    answers: list["Answer"]


@dataclass
class Answer:
    title: str
    is_correct: bool


class ThemeModel(db):
    __tablename__ = "themes"
    id = Column(BigInteger, primary_key=True)
    title = Column(VARCHAR(200), nullable=False, unique=True)
    questions = relation("QuestionModel", back_populates="theme")

    def __repr__(self):
        return f"<Theme(id='{self.id}', title='{self.titlei}')>"

    def set_attr(self, title: str) -> None:
        setattr(self, "title", title)


class QuestionModel(db):
    __tablename__ = "questions"
    id = Column(BigInteger, primary_key=True)
    title = Column(VARCHAR(200), nullable=False, unique=True)
    theme_id = Column(BigInteger, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    answers = relation("AnswerModel", back_populates="question")
    theme = relation("ThemeModel", back_populates="questions")

    def __repr__(self):
        return f"<Question(id='{self.id}', title='{self.title}')>"

    def to_question_dataclass(self) -> Question:
        return Question(
            id=self.id,
            title=self.title,
            theme_id=self.theme_id,
            answers=[
                Answer(
                    title=answer.title,
                    is_correct=answer.is_correct
                ) for answer in self.answers
            ]
        )


class AnswerModel(db):
    __tablename__ = "answers"
    id = Column(BigInteger, primary_key=True)
    title = Column(VARCHAR(250), nullable=False)
    is_correct = Column(BOOLEAN, nullable=False)
    question_id = Column(BigInteger, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    question = relation("QuestionModel", back_populates="answers")

    def __repr__(self):
        return f"<Answer(id='{self.id}', title='{self.titlei}')>"

