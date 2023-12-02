from datetime import datetime
from fir.helpers import generate_id


def default_profile_struct(name: str, description: str = "", tasks: list[dict] = []) -> dict:
    return {
        "id": generate_id(),
        "name": name,
        "description": description,
        "tasks": tasks,
        "config": {}
    }


def default_task_struct(name: str, tags: list[str] = [], status: str = "", due: str = "") -> dict:
    return {
        "id": generate_id(),
        "name": name,
        "tags": tags,
        "status": status,
        "added": datetime.now().strftime("%Y-%m-%d"),
        "modified": datetime.now().strftime("%Y-%m-%d"),
        "due": due
    }
