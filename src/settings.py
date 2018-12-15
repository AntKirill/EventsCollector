import os
from pathlib import Path

ROOT_DIRECTORY = Path(os.path.abspath(__file__)).parent.parent

LOG_FILENAME = 'events_collector.log'

DEBUG = False

# try:
#     from .local_settings import *
# except ImportError:
#     pass
