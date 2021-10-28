#!/usr/bin/env python
import argparse
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    argv = sys.argv

    if 'test' in argv:
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-f', '--future', action='store_true')
        args, argv = parser.parse_known_args(argv)
        from django.conf import settings
        settings.FUTURE_TESTS = args.future

    execute_from_command_line(argv)


if __name__ == '__main__':
    main()
