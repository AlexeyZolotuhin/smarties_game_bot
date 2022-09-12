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


class UpdateVictoriesGamerSchema(Schema):
    id_tguser = fields.Int(required=True)
    number_of_victories = fields.Int(required=True)


class RequestGamerSchema(Schema):
    id_tguser = fields.Int(required=True)
    username = fields.Str(required=True)


class GamerSchema(RequestGamerSchema):
    id = fields.Int(required=False)
    number_of_defeats = fields.Int(required=False)
    number_of_victories = fields.Int(required=False)


class ResponseGamerSchema(OkResponseSchema):
    data = fields.Nested(GamerSchema)


class GamerListSchema(Schema):
    gamers = fields.Nested(GamerSchema, many=True)


class ResponseGamerListSchema(OkResponseSchema):
    data = fields.Nested(GamerListSchema)
