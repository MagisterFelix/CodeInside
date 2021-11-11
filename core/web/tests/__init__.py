from django.conf import settings


def future(test_func):
    if settings.FUTURE_TESTS:
        return test_func
