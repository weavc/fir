
def generate_task_id(not_in: list[str] = []):
    return __generate_id(not_in=not_in)

def __generate_id(not_in: list[str] = [], i: int = 0):
    if i > 10000:
        raise Exception("Max iterations exceeded")
    import shortuuid
    from string import ascii_lowercase, digits
    shortuuid.set_alphabet(ascii_lowercase + digits)
    u = shortuuid.uuid()[:8]
    if u in not_in:
        return __generate_id(not_in=not_in, i=i + 1)
    return u


def str2bool(v, default=False):
    if v is None:
        return default
    elif v.lower() in ("yes", "y", "true", "1"):
        return True
    elif v.lower() in ("no", "n", "false", "0"):
        return False
    else:
        return default
