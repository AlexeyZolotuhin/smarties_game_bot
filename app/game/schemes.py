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


class UpdateDefeatsGamerSchema(Schema):
    id_tguser = fields.Int(required=True)
    number_of_defeats = fields.Int(required=True)


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


class RequestGameProgressSchema(Schema):
    id_gamer = fields.Int(required=True)
    id_gamesession = fields.Int(required=True)
    is_master = fields.Bool(required=False)


class GameProgressSchema(RequestGameProgressSchema):
    id = fields.Int(required=False)
    id_session = fields.Int(required=False)
    difficulty_level = fields.Int(required=True)
    gamer_status = fields.Str(required=True)  # Playing, Winner, Failed
    number_of_mistakes = fields.Int(required=True)
    number_of_right_answers = fields.Int(required=True)


class ResponseGameProgressSchema(OkResponseSchema):
    data = fields.Nested(GameProgressSchema)


class GameProgressListSchema(Schema):
    game_progresses = fields.Nested(GameProgressSchema, many=True)


class ResponseGameProgressListSchema(OkResponseSchema):
    data = fields.Nested(GameProgressListSchema)


class RequestChatIdSchema(Schema):
    chat_id = fields.Int(required=True)
    id_game_master = fields.Int(required=False)


class RequestTimeOutSchema(RequestChatIdSchema):
    time_for_answer = fields.Int(required=True)


class GameSessionSchema(RequestChatIdSchema):
    id = fields.Int(required=False)
    game_start = fields.DateTime(required=True)
    game_end = fields.DateTime(required=True)
    state = fields.Str(required=True)  # Active, Ended, Interrupted
    theme_id = fields.Int(required=True)  # -1 - without theme
    time_for_game = fields.Int(required=True)  # in minutes
    time_for_answer = fields.Int(required=True)  # in seconds
    game_progress = fields.Nested(GameProgressSchema, many=True)


class ResponseGameSessionSchema(OkResponseSchema):
    data = fields.Nested(GameSessionSchema)


class GameSessionListSchema(Schema):
    game_sessions = fields.Nested(GameSessionSchema, many=True)


class ResponseGameSessionListSchema(OkResponseSchema):
    data = fields.Nested(GameSessionListSchema)
