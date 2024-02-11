from ast import Tuple
from fir.context import Context
from fir.types.dtos import Error, TaskDto
from fir.utils.parse import parse_priority_from_arg

class SetHandlers:
    @staticmethod
    def status(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        set_status = context.profile.set_status(task, context.args.get("status"))
        if not set_status:
            return None, Error("Invalid status provided")

        context.profile.save()
        return task, None
    
    @staticmethod
    def link(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        task.link = context.args.get("link")

        context.profile.save()
        return task, None
    
    @staticmethod
    def priority(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, Error(err)

        passed, priority = parse_priority_from_arg(context.args.get("priority"))
        if not passed:
            return None, Error("Invalid priorty value. Must be an integer and between 1 - 999.")

        task.priority = priority

        context.profile.save()
        return task, None
    
    @staticmethod
    def description(context: Context) -> Tuple[TaskDto, Error]:
        task, err = context.profile.get_task(context.args.get("task_id"))
        if task is None:
            return None, err

        task.description = ' '.join(context.args.get("description"))

        context.profile.save()
        return task, None

