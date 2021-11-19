from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPoint, Qt
import os
import sys
import time
import string
import random
import threading
import webbrowser
from os.path import join
from pywitch_client_config import PyWitchClientConfig
from pywitch_client_manager import PyWitchClientManager
from _version import version
from _eula import eula

class PyWitchClientNoGui:
    def __init__(self):
        self.config = PyWitchClientConfig()
        self.token = self.config['authentication']['token']
        self.refresh_token = self.config['authentication']['refresh_token']
        self.channel = self.config['authentication']['channel']
        self.host = self.config['connection']['host']
        self.port = self.config['connection']['port']
        
        self.opt_check = {
            'tmi': self.config.getboolean('features', 'tmi'),
            'heat': self.config.getboolean('features', 'heat'),
            'redemptions': self.config.getboolean('features', 'redemptions'),
            'streaminfo': self.config.getboolean('features', 'streaminfo'),
        }
        
        self.eula = self.config.getboolean('eula','accept')
        self.config.save_config()
        
        if not self.eula:
            print (
                '(PyWitch Client) EULA not accepted. Please read EULA first '
                'and, if you agree with the conditions, change the '
                'value of [eula][accept] to True in pywitch_client_config.ini'
            )
            print('\nEULA:\n')
            print(eula)
            exit()
            

        self.manager = PyWitchClientManager(self.token, self.refresh_token, self.host, self.port)
        self.manager.start_flask()
        self.auth_url, self.auth_state = self.manager.get_auth_url()
        
    def start(self):
        self.validation = self.validation = self.manager.validate(self.token)
        if not self.validation:
            print('(PyWitch Client) Waiting for authorization...')
            webbrowser.open(self.auth_url)
        num = 0
        max_tries = 60
        interval = 3
        while num < max_tries and not self.validation:
            time.sleep(interval)
            num += 1
            self.token, self.refresh_token = self.manager.get_token('state')
            self.validation = self.manager.validate(self.token)
        if num >= max_tries:
            print(f'(PyWitch Client) Not able to authenticate!')
            return
        self.config['authentication']['token'] = self.token
        self.refresh_token = self.config['authentication']['refresh_token']
        self.config.save_config()
        
        self.channel_data = self.manager.verify_channel(self.channel)
        if not self.channel_data['login']:
            print(f'(PyWitch Client) Invalid channel "{self.channel}"!')
            return
        
        self.features = [k for k, v in self.opt_check.items() if v]
        
        self.manager.start_validator(self.token, self.refresh_token)
        self.manager.start_pywitch(self.channel, self.token, self.features)

        self.manager.run_forever()
