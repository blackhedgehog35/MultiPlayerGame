import configparser
from os.path import join


class Key:
    top: int
    bottom: int
    right: int
    left: int

    attack: int
    action1: int
    action2: int


class ConfigFile(configparser.ConfigParser):
    file = join('..', 'config.ini')
    key = Key()

    def __init__(self):
        super().__init__()
        self.update()

    def get_font_name(self):
        return self.get('FONT', 'family')

    def get_body_size(self):
        return self.getint('FONT', 'body-size')

    def get_title_size(self):
        return self.getint('FONT', 'title-size')

    def update(self):
        self.read(self.file)
        for section in ['DIRECTION--SETTINGS', 'ACTIONS--SETTINGS']:
            for option in self.options(section):
                setattr(self.key, option.replace(" ", ""), self.getint(section, option))

    def get_screen_size(self):
        return self.getint('SCREEN', 'width'), self.getint('SCREEN', 'height')

    def get_host(self):
        address = self.get('SERVER--SETTINGS', 'address')
        port = self.getint('SERVER--SETTINGS', 'port')
        return address, port

    def get_key(self):
        key = self.get("SERVER", 'key')
        if key == "":
            key = None
        else:
            pass
        return key

    def edit_value(self, section, option, value):
        self.set(section=section, option=option, value=value)
        with open(self.file, 'w') as configfile:
            self.write(configfile)

    def save_key(self, key):
        self.set("SERVER", "key", key)
        with open(self.file, "w") as configfile:
            self.write(configfile)
