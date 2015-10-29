#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')

import django
from django.core.management import call_command


if __name__ == '__main__':
    args = sys.argv[1:]

    django.setup()
    call_command('test', *args, verbosity=2, failfast=True)
