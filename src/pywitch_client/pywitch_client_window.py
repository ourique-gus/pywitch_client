from PyQt5.QtWidgets import (
    QLabel,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QApplication,
    QWidget,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QFormLayout,
    QMessageBox,
    QSizePolicy,
    QStyleFactory,
)
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


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class PyWitchClientApp:
    def __init__(self):
        self.app = QApplication([])
        self.style = 'Fusion'
        self.app.setStyle(self.style)
        self.window = PyWitchClientWindow(self.app)
        self.window.show()


class PyWitchClientWindow(QMainWindow):
    def __init__(self, app, *args, **kwargs):
        super(PyWitchClientWindow, self).__init__(*args, **kwargs)
        self.app = app
        self.setWindowTitle("PyWitch Client")
        self.setFixedWidth(225)

        self.config = PyWitchClientConfig()
        self.token = self.config['authentication']['token']
        self.refresh_token = self.config['authentication']['refresh_token']
        self.channel = self.config['authentication']['channel']
        self.host = self.config['connection']['host']
        self.port = self.config['connection']['port']
        self.eula = self.config.getboolean('eula','accept')

        self.manager = PyWitchClientManager(
            self.token, self.refresh_token, self.host, self.port
        )
        self.manager.start_flask()

        self.auth_url, self.auth_state = self.manager.get_auth_url()

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.setup_button()
        self.setup_writebox()
        self.setup_toggle_box()
        self.setup_about_button()

        self.check_for_updates()
        if str(version) != str(self.git_version):
            self.setup_update_button()
            
        if not self.eula:
            self.main_widget.setEnabled(False)
            self.popup_eula()

        self.setCentralWidget(self.main_widget)

    ##########################################################################

    def reset_widgets(self):
        self.button_widget.setText('Start PyWitch Server')
        self.button_widget.setEnabled(True)
        self.writebox_widget.setEnabled(True)
        for v in self.opt_check.values():
            v.setEnabled(True)
        self.image.setEnabled(True)

    ##########################################################################

    def setup_button(self):
        self.button_widget = QPushButton()
        self.button_widget.setText('Start PyWitch Server')
        self.button_widget.clicked.connect(self.click_button)
        self.layout.addWidget(self.button_widget)

    def click_button(self):
        self.button_widget.setEnabled(False)
        self.writebox_widget.setEnabled(False)
        for v in self.opt_check.values():
            v.setEnabled(False)
        self.image.setEnabled(False)
        if not self.manager.is_running:
            if self.token:
                self.button_widget.setText('Validating token...')
        thread = threading.Thread(target=self.button_clicked_thread, args=())
        thread.start()

    def button_clicked_thread(self):
        if not self.manager.is_running:
            self.validation = self.manager.validate(self.token)
            if not self.validation:
                self.button_widget.setText('Waiting for authorization...')
                webbrowser.open(self.auth_url)
            thread = threading.Thread(target=self.watch_for_token, args=(), daemon=True)
            thread.start()
        else:
            self.button_widget.setText('Stopping Pywitch Server...')
            self.manager.stop_all()
            self.reset_widgets()

    def watch_for_token(self, endpoint='state', interval=3, max_tries=60):
        num = 0
        while num < max_tries and not self.validation:
            time.sleep(interval)
            num += 1
            self.token, self.refresh_token = self.manager.get_token(endpoint)
            self.validation = self.manager.validate(self.token)
        if num >= max_tries:
            self.popup_error('Not able to authenticate!')
            return
        self.config['authentication']['token'] = self.token
        self.config['authentication']['refresh_token'] = self.refresh_token
        self.config.save_config()
        self.button_widget.setText('Starting PyWitch Server...')
        if not self.manager.validation:
            self.popup_error('Invalid token!')
            return
        self.channel_data = self.manager.verify_channel(self.channel)
        if not self.channel_data['login']:
            self.popup_error('Invalid channel!')
            return

        self.features = [k for k, v in self.opt_check.items() if v.isChecked()]
        self.manager.start_validator(self.token, self.refresh_token)
        self.manager.start_pywitch(self.channel, self.token, self.features)
        self.button_widget.setText('PyWitch Server Running!')
        self.button_widget.setEnabled(True)

    ##########################################################################

    def popup_error(self, msg):
        self.popup = PyWitchClientPopupError(msg, self.close_event)
        self.popup.button.clicked.connect(self.close_popup)
        self.popup.show()

    def close_popup(self):
        self.popup.close()

    def close_event(self):
        self.reset_widgets()

    ##########################################################################

    def setup_about_button(self):
        self.button_about_widget = QPushButton()
        self.button_about_widget.setText('About PyWitch')
        self.button_about_widget.clicked.connect(self.click_about_button)
        self.layout.addWidget(self.button_about_widget)

    def click_about_button(self):
        self.button_about_widget.setEnabled(False)
        self.about_popup = PyWitchClientPopupAbout(self.close_about_event)
        self.about_popup.button.clicked.connect(self.close_about_popup)
        self.about_popup.show()

    def close_about_popup(self):
        self.about_popup.close()

    def close_about_event(self):
        self.button_about_widget.setEnabled(True)

    ##########################################################################
    
    def popup_eula(self):
        self.popup_eula = PyWitchClientPopupEULA(self.close_eula_event)
        self.popup_eula.button_accept.clicked.connect(self.accept_eula_popup)
        self.popup_eula.button_reject.clicked.connect(self.reject_eula_popup)
        self.popup_eula.show()
        
    def accept_eula_popup(self):
        self.config['eula']['accept'] = str(True)
        self.eula = self.config.getboolean('eula','accept')
        self.popup_eula.close()

    def reject_eula_popup(self):
        self.config['eula']['accept'] = str(False)
        self.eula = self.config.getboolean('eula','accept')
        self.popup_eula.close()

    def close_eula_event(self):
        self.config.save_config()
        if not self.eula:
            self.app.closeAllWindows()
        else:
            self.main_widget.setEnabled(True)

    ##########################################################################

    def setup_update_button(self):
        self.button_update_widget = QPushButton()
        self.button_update_widget.setText('Update available! (click here)')
        self.button_update_widget.clicked.connect(self.click_update_button)
        self.layout.addWidget(self.button_update_widget)

    def click_update_button(self):
        webbrowser.open('https://github.com/ouriquegustavo/pywitch_client')

    ##########################################################################

    def setup_writebox(self):
        self.writebox_widget = QWidget()
        self.writebox_layout = QFormLayout()
        self.writebox_widget.setLayout(self.writebox_layout)

        self.wb_widget = QLineEdit()
        self.wb_widget.setText(self.channel)
        self.wb_widget.textChanged.connect(self.wb_changed)

        self.writebox_layout.addRow('Channel:', self.wb_widget)

        self.layout.addWidget(self.writebox_widget)

    def wb_changed(self, text):
        self.config['authentication']['channel'] = text
        self.channel = self.config['authentication']['channel']
        if not text:
            self.button_widget.setEnabled(False)
        else:
            self.button_widget.setEnabled(True)

    ##########################################################################

    def setup_toggle_box(self):
        self.opt_widget = QWidget()
        self.opt_layout = QVBoxLayout()
        self.opt_widget.setLayout(self.opt_layout)
        self.opt_check = {
            'tmi': QCheckBox("TMI"),
            'heat': QCheckBox("Heat"),
            'redemptions': QCheckBox("Redemptions"),
            'streaminfo': QCheckBox("Stream Information"),
        }
        for k, v in self.opt_check.items():
            v.setChecked(self.config.getboolean('features', k))
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
        self.opt_check['streaminfo'].toggled.connect(
            lambda: self.toggle_feature('streaminfo')
        )
        self.layout.addWidget(self.opt_widget)

        img_path = resource_path(join('logo', 'pywitch_logo.png'))

        pixmap = QPixmap(img_path)
        self.image = QLabel(self.opt_widget)
        self.image.setPixmap(pixmap)
        self.image.setFixedSize(pixmap.size())
        p = QPoint(130, 00)
        self.image.move(p)

    def toggle_feature(self, kind):
        state = self.opt_check[kind].isChecked()
        self.config['features'][kind] = str(state)
        self.config.save_config()


    ##########################################################################

    def closeEvent(self, event):
        self.config.save_config()
        self.app.closeAllWindows()

    ##########################################################################

    def check_for_updates(self):
        self.git_version = self.manager.get_version_in_repository()

    ##########################################################################


class PyWitchClientPopupError(QMainWindow):
    def __init__(self, msg, close_event):
        super().__init__()

        self.setWindowTitle('Error')
        self.close_event = close_event

        self.widget = QMessageBox()
        self.widget.setIcon(QMessageBox.Critical)
        self.widget.setText('Error!')
        self.widget.setInformativeText(msg)
        self.button = self.widget.addButton(QMessageBox.Ok)
        self.setCentralWidget(self.widget)

    def closeEvent(self, event):
        self.close_event()


class PyWitchClientPopupAbout(QMainWindow):
    def __init__(self, close_event):
        super().__init__()

        self.setWindowTitle('About')

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        self.close_event = close_event

        self.body = QLabel(
            "PyWitch Client is a GUI interface to PyWitch library combined "
            "with a Web Application Framework (Flask).\n\n"
            "Its main purpose is to provide HTTP endpoint to get the lastest "
            "Twitch events captured with PyWitch."
        )
        self.body.setWordWrap(True)

        self.author = QLabel(
            "\nAuthor: Gustavo Ourique (gleenus)\n\n" f"Version: {version}"
        )

        self.source = QLabel(
            '<a href="https://github.com/ouriquegustavo/pywitch">'
            'PyWitch Source (github)</a>'
        )
        self.source.setOpenExternalLinks(True)

        self.source_client = QLabel(
            f'<a href="https://github.com/ouriquegustavo/pywitch_client">'
            'PyWitch Client Source (github)</a>'
        )
        self.source_client.setOpenExternalLinks(True)

        self.button = QPushButton()
        self.button.setText('Close')

        self.layout.addWidget(self.body)
        self.layout.addWidget(self.author)
        self.layout.addWidget(self.source)
        self.layout.addWidget(self.source_client)
        self.layout.addWidget(self.button)

        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event):
        self.close_event()
        
class PyWitchClientPopupEULA(QMainWindow):
    def __init__(self, close_event):
        super().__init__()

        self.setWindowTitle('EULA')

        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout()
        self.buttons_widget.setLayout(self.buttons_layout)

        self.close_event = close_event

        self.body = QLabel(
            eula
        )
        self.body.setWordWrap(True)

        self.source = QLabel(
            '<a href="https://github.com/ouriquegustavo/pywitch_auth">'
            'PyWitch Authentication Service Source (github)</a>'
        )
        
        self.source.setOpenExternalLinks(True)
        
        self.extra = QLabel(
            "\nDo you accept these conditions?"
        )


        self.button_accept = QPushButton()
        self.button_reject = QPushButton()
        self.button_accept.setText('Accept')
        self.button_reject.setText('Reject')
        self.buttons_layout.addWidget(self.button_accept)
        self.buttons_layout.addWidget(self.button_reject)

        self.layout.addWidget(self.body)
        self.layout.addWidget(self.source)
        self.layout.addWidget(self.buttons_widget)

        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event):
        self.close_event()
