from marshmallow import Schema, fields, post_load, EXCLUDE, validate

from fir.types.dtos import ProfileDto, TaskDto, SettingsDto


class SettingsSchema(Schema):
    scope = fields.Str()
    profiles = fields.Dict(keys=fields.String(), values=fields.String())

    @post_load
    def make(self, data, **kwargs):
        return SettingsDto(**data)


class TaskSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(required=True, validate=validate.Length(min=8, max=8))
    name = fields.Str(required=True, validate=validate.Length(max=250))
    tags = fields.List(fields.String())
    status = fields.Str(required=True, default="")
    added = fields.Str(default="")
    modified = fields.Str(default="")
    due = fields.Str(default="")
    link = fields.Str(default="")
    description = fields.Str(default="")
    priority = fields.Field(strict=True, validate=validate.Range(min=0, max=999))
    assigned_to = fields.List(fields.String())

    @post_load
    def make_task(self, data, **kwargs):
        return TaskDto(**data)


class ProfileSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    name = fields.String(required=True, validate=validate.Length(max=250))
    description = fields.String(validate=validate.Length(max=250), default="")
    config = fields.Dict(keys=fields.String(), values=fields.String())
    tasks = fields.List(fields.Nested(TaskSchema()))

    @post_load
    def make_profile(self, data, **kwargs):
        return ProfileDto(**data)
