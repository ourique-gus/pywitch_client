from pywitch_client_app import PyWitchClientApp
import sys

if __name__ == "__main__":
    pywitch_client_app = PyWitchClientApp()
    sys.exit(pywitch_client_app.app.exec_())
