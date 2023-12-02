from dataclasses import dataclass, field
from datetime import datetime

from fir.helpers.dates import datetime_to_date_string


@dataclass
class TaskDto:
    id: str
    name: str
    status: str = ""
    due: str = ""
    tags: list[str] = field(default_factory=list[str])
    added: str = datetime_to_date_string(datetime.now())
    modified: str = datetime_to_date_string(datetime.now())


@dataclass
class ProfileDto:
    id: str
    name: str
    description: str
    tasks: list[TaskDto] = field(default_factory=list[TaskDto])
    config: dict[str, str] = field(default_factory=dict[str, str])


@dataclass
class SettingsDto:
    scope: str
