from re import match

from sqlalchemy.exc import IntegrityError
from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import docs, request_schema, response_schema, querystring_schema

from app.quiz.models import Answer
from app.quiz.schemes import (
    ListQuestionSchema,
    QuestionSchema,
    ThemeIdSchema,
    ThemeListSchema,
    ThemeSchema, ResponseThemeListSchema, ResponseThemeSchema, RequestThemeSchema, RequestQuestionSchema,
    ResponseQuestionSchema, ResponseListQuestionSchema,
)

from app.web.app import View
from app.web.decorators import require_auth
from app.web.utils import json_response


class ThemeAddView(View):
    @docs(tags=["Smarties game bot"], summary="ThemeAddView", description="Add new theme")
    @request_schema(RequestThemeSchema)
    @response_schema(ResponseThemeSchema, 200)
    @require_auth
    async def post(self):
        title = self.data["title"]
        try:
            theme = await self.store.quizzes.create_theme(title=title)
        except IntegrityError as e:
            match e.orig.pgcode:
                case '23505':
                    raise HTTPConflict(text='{"theme": ["theme already exists."]}')

        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    @docs(tags=["Smarties game bot"], summary="ThemeListView", description="Get list of all themes")
    @response_schema(ResponseThemeListSchema, 200)
    @require_auth
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data=ThemeListSchema().dump({"themes": themes}))


class QuestionAddView(View):
    @docs(tags=["Smarties game bot"], summary="QuestionAddView", description="Add new question")
    @request_schema(RequestQuestionSchema)
    @response_schema(ResponseQuestionSchema)
    @require_auth
    async def post(self):
        title = self.data["title"]
        theme_id = self.data["theme_id"]
        answers = [
            Answer(
                title=a["title"],
                is_correct=a["is_correct"],
            ) for a in self.data["answers"]
        ]

        if len(set([a.is_correct for a in answers])) == 1:
            raise HTTPBadRequest(text='wrong answers')

        try:
            question = await self.store.quizzes.create_question(
                title=title,
                theme_id=theme_id,
                answers=answers,
            )
        except IntegrityError as e:
            match e.orig.pgcode:
                case "23503":
                    raise HTTPNotFound(text='{"theme_id": ["theme with pointed them_id does not exist."]}')
                case "23505":
                    raise HTTPConflict(text='{"question": ["question already exists."]}')

        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(View):
    @docs(tags=["Smarties game bot"], summary="QuestionListView",
          description="Get list of questions all or by theme_id")
    @querystring_schema(ThemeIdSchema)
    @response_schema(ResponseListQuestionSchema)
    @require_auth
    async def get(self):
        theme_id = self.data.get("theme_id")
        questions = await self.store.quizzes.list_questions(theme_id=theme_id)
        data = {"questions": [QuestionSchema().dump(question) for question in questions]}

        return json_response(data=data)
