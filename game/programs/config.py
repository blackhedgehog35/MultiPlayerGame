import configparser
from os.path import join


class ConfigFile(configparser.ConfigParser):
    file = join('..', 'config.ini')

    def __init__(self):
        super().__init__()
        self.data_file = self.read(self.file)

    def get_screen_size(self):
        return self.getint('SCREEN', 'width'), self.getint('SCREEN', 'height')

    def get_host(self):
        address = self.get('SERVER', 'address')
        port = self.getint('SERVER', 'port')
        return address, port

    def edit_value(self, section, option, value):
        self.set(section=section, option=option, value=value)
        with open(self.file, 'w') as configfile:
            self.write(configfile)
