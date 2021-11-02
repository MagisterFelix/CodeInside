from pytz import timezone


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def convert_datetime(datetime, time_zone):
    return datetime.astimezone(timezone(time_zone)).strftime('%m/%d/%Y %H:%M')
