from marshmallow import Schema, fields

from app.web.schema import OkResponseSchema


class RequestAdminSchema(Schema):
    login = fields.Str(required=True)
    password = fields.Str(required=True)


class AdminSchema(Schema):
    id = fields.Int(required=False)
    login = fields.Str(required=True)


class ResponseAdminSchema(OkResponseSchema):
    data = fields.Nested(AdminSchema)



