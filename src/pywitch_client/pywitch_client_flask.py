import requests
from flask import Flask, request

class PyWitchClientFlas():
    def __init__(self, host='127.0.0.1', port=13486):
        self.host = host
        self.port = port
        self.app = Flask('app')
        
    def start():
        kwargs = {
            'host': self.host
            'port': self.port,
            'threaded': True,
            'use_reloader': False,
            'debug': False,
        }

        self.thread = threading.Thread(
            target=flask_app.run,
            daemon=True,
            kwargs=kwargs
        )
        self.thread.start()        
