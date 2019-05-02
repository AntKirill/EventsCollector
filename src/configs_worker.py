import json

import settings


def load_configs_from_disc():
    with settings.CLIENTS_CONFIG_FILE['configs'].open(mode='r') as configs_file:
        data = json.load(configs_file)
        return data


def _validate_configs(c):
    return True


def update_configs_on_disc(new_configs):
    if type(new_configs) is not dict:
        return False
    if not _validate_configs(new_configs):
        return False
    with settings.CLIENTS_CONFIG_FILE['configs'].open(mode='w') as configs_file:
        json.dump(new_configs, configs_file)
        return True
