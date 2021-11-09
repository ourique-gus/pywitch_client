from PyQt5.QtWidgets import QApplication, QStyleFactory
from pywitch_client_window import PyWitchClientWindow


class PyWitchClientApp:
    def __init__(self):
        self.app = QApplication([])
        self.style = 'Fusion'
        self.app.setStyle(QStyleFactory.create(self.style))
        self.window = PyWitchClientWindow(self.app)
        self.window.show()
