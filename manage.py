#!/usr/bin/env python
import sys
from settings import configure_settings

# Show warnings about django deprecations - uncomment for version upgrade testing
import warnings
from django.utils.deprecation import RemovedInNextVersionWarning
warnings.filterwarnings('always', category=DeprecationWarning)
warnings.filterwarnings('always', category=PendingDeprecationWarning)
warnings.filterwarnings('always', category=RemovedInNextVersionWarning)

if __name__ == '__main__':
    configure_settings()

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
