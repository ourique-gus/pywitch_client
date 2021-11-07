from PyQt5.QtWidgets import QApplication, QStyleFactory
from pywitch_client_window import PyWitchClientWindow

import threading
import sys
import time

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create('Fusion'))
    window = PyWitchClientWindow()
    window.show()
    app.exec_()
