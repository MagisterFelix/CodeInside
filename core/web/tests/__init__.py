from django.conf import settings

STRONG_PASSWORD = '53175bcc0524f37b47062faf5da28e3f8eb91d51'


def future(test_func):
    if settings.FUTURE_TESTS:
        return test_func
