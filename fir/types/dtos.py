from dataclasses import dataclass, field
from datetime import datetime

from marshmallow import Schema, fields, post_load, validate, EXCLUDE

from fir.helpers.dates import datetime_to_date_string
from fir.types.config_options import ConfigOptions


@dataclass
class TaskDto:
    id: str
    name: str
    status: str = ""
    due: str = ""
    tags: list[str] = field(default_factory=list[str])
    added: str = datetime_to_date_string(datetime.now())
    modified: str = datetime_to_date_string(datetime.now())
    link: str = ""
    description: str = ""
    priority: int = 100
    assigned_to: list[str] = field(default_factory=list[str])

    class Schema(Schema):
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

@dataclass
class StatusDto:
    name: str
    color: str
    priority: int = 100
    
    class Schema(Schema):
        class Meta:
            unknown = EXCLUDE

        name = fields.String(required=True, validate=validate.Length(max=50))
        color = fields.String(required=True, validate=validate.Length(max=20))
        priority = fields.Field(strict=True, validate=validate.Range(min=0, max=999))

        @post_load
        def make_task(self, data, **kwargs):
            return StatusDto(**data)


@dataclass
class ProfileDto:
    name: str
    description: str
    config: dict[ConfigOptions, str] = field(default_factory=dict[ConfigOptions, str])
    tasks: list[TaskDto] = field(default_factory=list[TaskDto])
    statuses: list[StatusDto] = field(default_factory=list[StatusDto])

    class Schema(Schema):
        class Meta:
            unknown = EXCLUDE

        name = fields.String(required=True, validate=validate.Length(max=250))
        description = fields.String(validate=validate.Length(max=250), default="")
        config = fields.Dict(keys=fields.String(), values=fields.String())
        tasks = fields.List(fields.Nested(TaskDto.Schema()))
        statuses = fields.List(fields.Nested(StatusDto.Schema()))

        @post_load
        def make_profile(self, data, **kwargs):
            return ProfileDto(**data)


@dataclass
class SettingsDto:
    scope: str
    profiles: dict[str, str] = field(default_factory=dict[str, str])

    class Schema(Schema):
        scope = fields.Str()
        profiles = fields.Dict(keys=fields.String(), values=fields.String())

        @post_load
        def make(self, data, **kwargs):
            return SettingsDto(**data)