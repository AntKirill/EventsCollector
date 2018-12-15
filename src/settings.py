from pathlib import Path

ROOT_DIRECTORY = Path()

LOG_FILENAME = 'events_collector.log'

DEBUG = False

try:
    from .local_settings import *
except ImportError:
    pass
