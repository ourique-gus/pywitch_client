from PyQt5.QtWidgets import QApplication
from pywitch_client_window import PyWitchClientWindow

import threading
import sys
import time



# https://id.twitch.tv/oauth2/authorize?response_type=code&client_id=9lzu5wqst0swbinmvqpqu80failj3l&redirect_uri=https://pywitch-auth.herokuapp.com/authenticate&scope=channel:read:redemptions%20channel:read:redemptions%20user:read:email%20chat:edit%20chat:read&state=12345678

#   Creating instance of QApplication
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyWitchClientWindow()
    window.show()
    app.exec_()

