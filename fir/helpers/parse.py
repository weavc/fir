from fir.helpers.dates import str_to_date_string


def parse_date_from_arg(date: str) -> (bool, str):
    dt = ""
    if date:
        try:
            dt = str_to_date_string(date)
        except ValueError:
            return False, None

    return True, dt


def parse_priority_from_arg(priority: str) -> (bool, int):
    try:
        p = int(priority)
        if p < 1 or p > 999:
            raise Exception()
        return True, p
    except BaseException:
        return False, 0
