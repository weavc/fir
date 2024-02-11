from ast import Tuple
from fir.context import Context
from fir.types.dtos import Error, StatusDto, TaskDto
from fir.utils.parse import parse_priority_from_arg

class StatusHandlers:
    @staticmethod
    def new(context: Context) -> Tuple[StatusDto, Error]:
        color = context.args.get("color", "light_blue")
        hide_status = context.args.get("hide_status", True)
        passed, order = parse_priority_from_arg(context.args.get("order"), 600)
        if not passed:
            err = Error("Invalid priorty value. Must be an integer and between 1 - 999.")
            return None, err

        status = StatusDto(context.args.get("status"), color, order=order, hide_by_default=hide_status)
        context.profile.data.statuses.append(status)

        context.profile.save()
        return status, None

    @staticmethod
    def colour(context: Context) -> Tuple[StatusDto, Error]:
        status = context.profile.get_status_by_name(context.args.get("status"))
        if status is None:
            return None, Error("Could not find status.")

        status.color = context.args.get("color", "light_blue")

        context.profile.save()
        return status, None

    @staticmethod
    def order(context: Context) -> Tuple[StatusDto, Error]:
        status = context.profile.get_status_by_name(context.args.get("status"))
        if status is None:
            return None, Error("Could not find status.")

        passed, order = parse_priority_from_arg(context.args.get("order"), 600)
        if not passed:
            return None, Error("Invalid priorty value. Must be an integer and between 1 - 999.")

        status.order = order

        context.profile.save()
        return status, None
    
    @staticmethod
    def hide(context: Context) -> Tuple[StatusDto, Error]:
        status = context.profile.get_status_by_name(context.args.get("status"))
        if status is None:
            return None, Error("Could not find status.")

        status.hide_by_default = not status.hide_by_default

        context.profile.save()
        return status, None
    
    @staticmethod
    def rm(context: Context) -> Tuple[StatusDto, Error]:
        status = context.profile.get_status_by_name(context.args.get("status"))
        if status is None:
            return None, Error("Could not find status.")

        context.profile.data.statuses.remove(status)

        context.profile.save()
        return status, None