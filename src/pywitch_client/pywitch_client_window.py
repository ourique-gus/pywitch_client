from PyQt5.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QMainWindow,
    QApplication,
    QWidget,
    QPushButton,
    QCheckBox,
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QPoint
import zlib
import time
import string
import random
import threading
import webbrowser
from os.path import isfile, join
from configparser import ConfigParser
from pywitch_client_manager import PyWitchClientManager


class PyWitchClientWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(PyWitchClientWindow, self).__init__(*args, **kwargs)
        self.setWindowTitle("PyWitch Client")
        self.setFixedWidth(225)
        
        self.read_config()
        self.token = self.config['authentication']['token']
        
        self.manager = PyWitchClientManager(self.token)
        self.auth_url, self.auth_state = self.manager.get_auth_url()
        print(self.auth_url)
        
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
        self.setup_button()        
        self.setup_toggle_box()

        self.setCentralWidget(self.main_widget)
        
##############################################################################

    def setup_button(self):
        self.button_widget = QPushButton()
        self.button_widget.setText('Start PyWitch Server')
        self.button_widget.clicked.connect(self.click_button)
        self.layout.addWidget(self.button_widget)
        
    def click_button(self):
        self.button_widget.setEnabled(False)
        for v in self.opt_check.values():
            v.setEnabled(False)
        if not self.manager.is_running:
            if self.token:
                self.button_widget.setText('Validating token...')
        thread=threading.Thread(target=self.button_clicked_thread, args=())
        thread.start()
                
    def button_clicked_thread(self):
        if not self.manager.is_running:
            validation = self.manager.validate(self.token)
            if not self.token:
                self.button_widget.setText('Waiting for authorization...')
                webbrowser.open(self.auth_url)
            thread=threading.Thread(target=self.watch_for_token, args=())
            thread.start()
            
    def watch_for_token(self, endpoint='state', interval = 3, max_tries=60):
        num=0
        while num < max_tries and not self.token:
            time.sleep(interval)
            num += 1
            self.token = self.manager.get_token(endpoint)
        self.config['authentication']['token'] = self.token
        self.save_config()
        self.button_widget.setText('Starting PyWitch Server...')
        self.manager.start_flask()
            
        
##############################################################################
        
    def setup_toggle_box(self):
        self.opt_widget = QWidget()
        self.opt_layout = QVBoxLayout()
        self.opt_widget.setLayout(self.opt_layout)
        self.opt_check = {
            'tmi': QCheckBox("TMI"),
            'heat': QCheckBox("Heat"),
            'redemptions': QCheckBox("Redemptions"),
            'stream_info': QCheckBox("Stream Information"),
        }
        for k, v in self.opt_check.items():
            v.setChecked(self.config.getboolean('features',k))
            v.setToolTip(f'{self.manager.server_url}/{k}')
            self.opt_layout.addWidget(v)
        
        self.opt_check['tmi'].toggled.connect(
            lambda: self.toggle_feature('tmi')
        )
        self.opt_check['heat'].toggled.connect(
            lambda: self.toggle_feature('heat')
        )
        self.opt_check['redemptions'].toggled.connect(
            lambda: self.toggle_feature('redemptions')
        )
        self.opt_check['stream_info'].toggled.connect(
            lambda: self.toggle_feature('stream_info')
        )
        self.layout.addWidget(self.opt_widget)
        
        pixmap = QPixmap(join('logo','pywitch_logo.png'))
        self.image = QLabel(self.opt_widget)
        self.image.setPixmap(pixmap)
        self.image.setFixedSize(pixmap.size())
        p = QPoint(130, 00)
        self.image.move(p)
        
    def toggle_feature(self,kind):
        state=self.opt_check[kind].isChecked()
        self.config['features'][kind] = str(state)
        self.save_config()
        
##############################################################################
        
    def save_config(self):
        if not hasattr(self,'config'):
            self.read_config()
        with open(self.config_file, 'w') as open_cf:
            self.config.write(open_cf)
        
    def read_config(self, config_file = 'pywitch_client_config.ini'):
        self.config_file = config_file
        self.config = ConfigParser()
        if isfile(self.config_file):
            self.config.read(config_file)
        else:            
            self.config['authentication'] = {'token': ''}
            self.config['features'] = {
                'tmi': True,
                'heat': True,
                'redemptions': True,
                'stream_info': True,
            }
            with open(self.config_file, 'w') as open_cf:
                self.config.write(open_cf)
            
            
            
