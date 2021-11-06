import json
import string
import random
import requests
import threading
from pywitch import validate_token
from flask import Flask, request

events={
    'tmi': {},
    'heat': {},
    'redemptions': {},
    'stream_info': {},

}

app = Flask('app')

@app.route('/<kind>')
def route_tmi(kind):
    if kind not in events:
        return '{}'
    return json.dumps(events[kind], ensure_ascii=False)

class PyWitchClientManager:
    def __init__(
        self,
        token = None,
        host='127.0.0.1',
        port=13486,
        auth_server='https://pywitch-auth.herokuapp.com',
        auth_client_id='9lzu5wqst0swbinmvqpqu80failj3l',
        auth_scopes=[
            'channel:read:redemptions',
            'channel:read:redemptions',
            'user:read:email',
            'chat:edit',
            'chat:read',
        ],
    ):
        self.token = token
        self.host = host
        self.port = port
        self.auth_server = auth_server
        self.auth_client_id = auth_client_id
        self.auth_scopes = auth_scopes

        if self.port:
            self.server_url = f'{self.host}:{self.port}'
        else:
            self.server_url = self.host
            
        self.is_running = False
        
    def get_auth_url(self, auth_endpoint='authenticate'):
        self.auth_endpoint = auth_endpoint
        self.auth_state_valid = string.ascii_letters + string.digits
        self.auth_state_lenght = 128
        self.auth_state = ''.join(
            [
                random.choice(self.auth_state_valid)
                for i in range(self.auth_state_lenght)
            ]
        )
        self.auth_scopes_str = '%20'.join(self.auth_scopes)
        self.auth_url = (
            'https://id.twitch.tv/oauth2/authorize'
            '?response_type=code'
            f'&client_id={self.auth_client_id}'
            f'&redirect_uri={self.auth_server}/{self.auth_endpoint}'
            f'&scope={self.auth_scopes_str }'
            f'&state={self.auth_state}'
        )
        return self.auth_url, self.auth_state

    def get_token(self, state_endpoint='state'):
        self.state_endpoint = state_endpoint
        url = f'{self.auth_server}/{self.state_endpoint}'
        params = {'state': self.auth_state}
        response = requests.get(url, params=params)
        data = response.json()
        token = data.get('access_token')
        return token

    def validate(self, token):
        try:
            self.validation, self.helix_headers = validate_token(token)
        except:
            self.validation = {}
        return self.validation
        
    def start_flask(self):
        kwargs = {
            'host': self.host,
            'port': self.port,
            'threaded': True,
            'use_reloader': False,
            'debug': False,
        }

        self.thread = threading.Thread(
            target=app.run, daemon=True, kwargs=kwargs
        )
        self.thread.start()
        
