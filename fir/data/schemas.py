from dataclasses import dataclass, field
from marshmallow import Schema, fields, post_load, EXCLUDE, pre_load, validate

from fir.data.dtos import Profile, Task

class TaskSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Str(required=True, validate=validate.Length(min=8, max=8))
    name = fields.Str(required=True, validate=validate.Length(max=250))
    tags = fields.List(fields.String())
    status = fields.Str(default="")
    added = fields.Str(default="")
    modified = fields.Str(default="")
    due = fields.Str(default="")

    @post_load
    def make_task(self, data, **kwargs):
        return Task(**data)

class ProfileSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.String(required=True, validate=validate.Length(min=8, max=8))
    name = fields.String(required=True, validate=validate.Length(max=250))
    description = fields.String(validate=validate.Length(max=250), default="")
    tasks = fields.List(fields.Nested(TaskSchema()))
    config = fields.Dict(keys=fields.String(), values=fields.String())

    @post_load
    def make_profile(self, data, **kwargs):
        return Profile(**data)