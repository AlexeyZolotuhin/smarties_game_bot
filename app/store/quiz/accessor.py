from app.base.base_accessor import BaseAccessor
from sqlalchemy import String, and_, delete, or_, select, distinct, update, insert
from sqlalchemy.orm import joinedload
from app.quiz.models import (
    Answer,
    Question,
    Theme, ThemeModel, AnswerModel, QuestionModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        new_theme = ThemeModel(title=title)
        await self.make_add_query(new_theme)
        return Theme(id=new_theme.id, title=new_theme.title)

    async def get_theme_by_title(self, title: str) -> Theme | None:
        query = select(ThemeModel).where(ThemeModel.title == title)
        result = (await self.make_get_query(query)).scalars().first()

        if not result:
            return

        return Theme(id=result.id, title=result.title)

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        query = select(ThemeModel).where(ThemeModel.id == id_)
        result = (await self.make_get_query(query)).scalars().first()

        if not result:
            return

        return Theme(id=result.id, title=result.title)

    async def list_themes(self) -> list[Theme]:
        query = select(ThemeModel)
        result = (await self.make_get_query(query)).scalars().unique()

        if not result:
            return []

        return [Theme(id=theme.id, title=theme.title) for theme in result]

    async def create_answers(self, question_id: int, answers: list[Answer]) -> list[Answer]:
        res_answers = []
        for answer in answers:
            answer_model = AnswerModel()
            answer_model.set_attr(title=answer.title,
                                  question_id=question_id,
                                  is_correct=answer.is_correct)
            await self.make_add_query(answer_model)
            res_answers.append(answer)
        return res_answers

    async def create_question(self, title: str, theme_id: int, answers: list[Answer]) -> Question:
        new_question = QuestionModel(
            title=title,
            theme_id=theme_id,
            answers=[
                AnswerModel(
                    title=answer.title,
                    is_correct=answer.is_correct,
                ) for answer in answers
            ],
        )
        await self.make_add_query(new_question)
        return new_question.to_question_dataclass()

    async def get_question_by_title(self, title: str) -> Question | None:
        query = select(QuestionModel) \
            .where(QuestionModel.title == title) \
            .options(joinedload(QuestionModel.answers))
        result = await self.make_get_query(query)

        obj: QuestionModel | None = result.scalar().first()
        if obj is None:
            return
        return obj.to_question_dataclass()

    async def list_questions(self, theme_id: int | None = None) -> list[Question]:
        query = select(QuestionModel)

        if theme_id:
            query = select(QuestionModel).where(QuestionModel.theme_id == theme_id)

        results = await self.make_get_query(query.options(joinedload(QuestionModel.answers)))

        return [Question(
            id=q.id,
            title=q.title,
            theme_id=q.theme_id,
            answers=[
                Answer(
                    title=a.title,
                    is_correct=a.is_correct,
                ) for a in q.answers
            ]
        ) for q in results.scalars().unique()
        ]
