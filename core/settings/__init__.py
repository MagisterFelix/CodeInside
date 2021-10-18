from .base import *

try:
    from .dev import *
except ImportError:
    print('You need the [SECRET_KEY]')
