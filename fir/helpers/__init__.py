def generate_id():
    import shortuuid
    return shortuuid.uuid()[:8]


def str2bool(v):
    return v.lower() in ("yes", "true", "1")
