from fir.helpers.dates import str_to_date_string


def parse_date_from_arg(date: str) -> (bool, str):
    dt = ""
    if date:
        try:
            dt = str_to_date_string(date)
        except ValueError:
            return False, None

    return True, dt


def parse_priority_from_arg(priority: str, default: int = 0) -> (bool, int):
    return parse_int_from_arg(priority, default, 1, 999)


def parse_int_from_arg(value: str, default: int = 0, min: int = None, max: int = None) -> (bool, int):
    if value is None and default != 0:
        return True, default
    try:
        p = int(value)
        if min and p < min:
            raise Exception()
        if max and p > max:
            raise Exception()
        return True, p
    except BaseException:
        return False, 0
