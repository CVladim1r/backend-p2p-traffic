from datetime import datetime

def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M:%S")