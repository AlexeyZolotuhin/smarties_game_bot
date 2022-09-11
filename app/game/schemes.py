from marshmallow import Schema, fields
from app.web.schema import OkResponseSchema


class RequestPathwaySchema(Schema):
    color = fields.Str(required=True)
    max_questions = fields.Int(required=True)
    max_mistakes = fields.Int(required=True)


class PathwaySchema(RequestPathwaySchema):
    id = fields.Int(required=False)


class ResponsePathwaySchema(OkResponseSchema):
    data = fields.Nested(PathwaySchema)


class PathwayListSchema(Schema):
    pathways = fields.Nested(PathwaySchema, many=True)


class ResponsePathwayListSchema(OkResponseSchema):
    data = fields.Nested(PathwayListSchema)
