from configparser import ConfigParser
from os.path import isfile


class PyWitchClientConfig(ConfigParser):
    def __init__(self, config_file='pywitch_client_config.ini'):
        super(ConfigParser, self).__init__()
        self.config_file = config_file
        self.read_config()

    def save_config(self):
        with open(self.config_file, 'w') as open_cf:
            print('here', self.config_file)
            self.write(open_cf)

    def read_config(self):
        if isfile(self.config_file):
            self.read(self.config_file)
        else:
            self['authentication'] = {'token': '', 'channel': 'gleenus'}
            self['connection'] = {'host': '127.0.0.1', 'port': 13486}
            self['features'] = {
                'tmi': True,
                'heat': True,
                'redemptions': True,
                'stream_info': True,
            }
            with open(self.config_file, 'w') as open_cf:
                self.write(open_cf)
