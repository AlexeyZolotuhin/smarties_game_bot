from marshmallow import Schema, fields

from app.web.schema import OkResponseSchema


class RequestThemeSchema(Schema):
    title = fields.Str(required=True)


class ThemeSchema(RequestThemeSchema):
    id = fields.Int(required=False)


class ResponseThemeSchema(OkResponseSchema):
    data = fields.Nested(ThemeSchema)


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)


class ResponseThemeListSchema(OkResponseSchema):
    data = fields.Nested(ThemeListSchema)


class RequestQuestionSchema(Schema):
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested("AnswerSchema", many=True, required=True)


class QuestionSchema(RequestQuestionSchema):
    id = fields.Int(required=False)


class ResponseQuestionSchema(OkResponseSchema):
    data = fields.Nested(QuestionSchema)


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class ThemeIdSchema(Schema):
    theme_id = fields.Int(required=False)


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)


class ResponseListQuestionSchema(OkResponseSchema):
    data = fields.Nested(ListQuestionSchema)
