import configparser


class ConfigFile(configparser.ConfigParser):
    def __init__(self):
        super().__init__()
        self.data_file = self.read('../config.ini')

    def get_value(self, section, variable_name):
        return self.data_file[section][variable_name]
