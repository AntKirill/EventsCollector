import json


def create_default_file():
    default_data = {
        'delete_expired': False,
        'data_only': False,
        'event_names': r'event*',
        'timezone': 0
    }
    return default_data


class Config_Handler:
    def __init__(self):
        self.data = dict()

    def __update_settings_file(self):
        with open("config_file.json", "w") as write_file:
            json.dump(self.data, write_file)

    def __get_settings_from_file(self):
        try:
            file = open("config_file.json", "r")
        except IOError as e:
            self.data = create_default_file()
            self.__update_settings_file()
        else:
            with file:
                self.data = json.load(file)

    def get_settings_map(self):

        if (not self.data):  # словарь в bool это пуст ли он
            self.__get_settings_from_file()

        return self.data

    def update_settings_map(self, updated_values):
        self.get_settings_map()
        self.data.update(updated_values)
        self.__update_settings_file()
