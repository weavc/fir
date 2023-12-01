from datetime import datetime, date

def str_to_date_string(dt: str):
    return datetime.strptime(dt, "%Y-%m-%d").date().strftime("%Y-%m-%d")

def datetime_to_date_string(dt: datetime):
    return datetime.strftime(dt, "%Y-%m-%d %H:%M:%S")