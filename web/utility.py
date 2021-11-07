from django.db.models import Case, CharField, Value, When

from pytz import timezone


class DotDict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class WithChoices(Case):
    def __init__(self, model, field, condition=None, then=None, **lookups):
        choices = dict(model._meta.get_field(field).flatchoices)
        whens = [When(**{field: k, 'then': Value(v)}) for k, v in choices.items()]
        return super().__init__(*whens, output_field=CharField())


def convert_datetime(datetime, time_zone):
    return datetime.astimezone(timezone(time_zone)).strftime('%m/%d/%Y %H:%M')
