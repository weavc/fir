from dataclasses import dataclass, field

@dataclass
class Task:
    id: str
    name: str
    status: str
    added: str
    modified: str
    due: str
    tags: list[str] = field(default_factory=list[str])

@dataclass
class Profile:
    id: str
    name: str
    description: str
    tasks: list[Task] = field(default_factory=list[Task])
    config: dict[str, str] = field(default_factory=dict[str, str])