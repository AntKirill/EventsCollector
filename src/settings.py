import os
from pathlib import Path

ROOT_DIRECTORY = Path(os.path.abspath(__file__)).parent.parent

LOG_FILENAME = 'events_collector.log'

DEBUG = False

try:
    from local_settings import *
except ImportError:
    pass

SECRET_DIRECTORY = ROOT_DIRECTORY / 'resources' / 'secret'
SECRET_DIRECTORY.mkdir(parents=True, exist_ok=True)

CLIENTS_CONFIG_DIRECTORY = ROOT_DIRECTORY / 'resources' / 'clients'
CLIENTS_CONFIG_DIRECTORY.mkdir(parents=True, exist_ok=True)

CREDENTIALS_FILE = {
    'google_calendar': (SECRET_DIRECTORY / 'google_calendar_credentials.json').resolve(),
    'trello': (SECRET_DIRECTORY / 'trello_credentials.json').resolve()
}

CLIENTS_CONFIG_FILE = {
    'configs': (CLIENTS_CONFIG_DIRECTORY / 'configs.json').resolve()
}
