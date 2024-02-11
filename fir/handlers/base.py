from ast import Tuple
from datetime import datetime
from fir.context import Context
from fir.types.dtos import Error, TaskDto
from fir.utils import generate_task_id
from fir.utils.dates import datetime_to_date_string
from fir.utils.parse import parse_date_from_arg, parse_priority_from_arg

class BaseHandlers:
    @staticmethod
    def create_task(context: Context) -> Tuple[TaskDto, Error]:
        status = context.profile.data.config.get("status.default", "")
        if context.args.get("status"):
            status = context.args.get("status")

        success, due = parse_date_from_arg(context.args.get("due"))
        if not success:
            return None, Error("Unable to parse date from due date")

        task_name = ' '.join(context.args.get("task_name"))
        task = TaskDto(generate_task_id(not_in=[t.id for t in context.profile.data.tasks]), task_name, due=due)

        set_status = context.profile.set_status(task, status)
        if not set_status:
            return None, Error("Invalid status provided")

        if (context.args.get("priority")):
            passed, priority = parse_priority_from_arg(context.args.get("priority"))
            if not passed:
                return None, Error("Invalid priorty value. Must be an integer and between 1 - 999.")
            task.priority = priority
        if context.args.get("description"):
            task.description = context.args.get("description")
        if context.args.get("link"):
            task.link = context.args.get("link")

        context.profile.data.tasks.append(task)
        context.profile.save()
        return task, None

    @staticmethod
    def modify_task(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        if context.args.get("status") is not None:
            set_status = context.profile.set_status(task, context.args.get("status"))
            if not set_status:
                return None, Error("Invalid status provided")
        if context.args.get("task_name") is not None:
            task.name = context.args.get("task_name")
        if context.args.get("due"):
            success, due = parse_date_from_arg(context.args.get("due"))
            if not success:
                return None, Error("Unable to parse date from due date")
            task.due = due
        if (context.args.get("priority")):
            passed, priority = parse_priority_from_arg(context.args.get("priority"))
            if not passed:
                return None, Error("Invalid priorty value. Must be an integer and between 1 - 999.")
            task.priority = priority
        if context.args.get("description"):
            task.description = context.args.get("description")
        if context.args.get("link"):
            task.link = context.args.get("link")

        task.modified = datetime_to_date_string(datetime.now())
        context.profile.save()
        return task, None
    
    @staticmethod
    def remove_task(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        context.profile.data.tasks.remove(task)
        context.profile.save()

        return task, None

    @staticmethod
    def add_tag(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        tags = context.args.get("tags")

        for t in tags:
            if t not in task.tags:
                task.tags.append(t)

        context.profile.save()
        return task, None

    @staticmethod
    def rm_tag(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        tags = context.args.get("tags")

        for t in tags:
            if t in task.tags:
                task.tags.remove(t)

        context.profile.save()
        return task, None

    @staticmethod
    def add_assigned(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        assignees = context.args.get("assignee")

        for a in assignees:
            if a not in task.assigned_to:
                task.assigned_to.append(a)

        context.profile.save()
        return task, None

    @staticmethod
    def rm_assigned(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        assignees = context.args.get("assignee")

        for a in assignees:
            if a in task.assigned_to:
                task.assigned_to.remove(a)

        context.profile.save()
        return task, None