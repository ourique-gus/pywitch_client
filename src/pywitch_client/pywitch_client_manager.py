import json
import time
import string
import random
import requests
import threading
from flask import Flask, request
from pywitch import (
    validate_token,
    get_user_info,
    PyWitchTMI,
    PyWitchHeat,
    PyWitchRedemptions,
    PyWitchStreamInfo,
)

valid_char = string.ascii_letters + string.digits


def random_string(length):
    return ''.join([random.choice(valid_char) for i in range(length)])


events = {
    'tmi': {},
    'heat': {},
    'redemptions': {},
    'streaminfo': {},
}


def tmi_callback(data):
    data.pop('event_raw')
    data['pywitch_id'] = random_string(64)
    print(data)
    events['tmi'] = json.dumps(data, ensure_ascii=False)


def heat_callback(data):
    data.pop('event_raw')
    data['pywitch_id'] = random_string(64)
    events['heat'] = json.dumps(data, ensure_ascii=False)


def redemptions_callback(data):
    data.pop('event_raw')
    data['pywitch_id'] = random_string(64)
    events['redemptions'] = json.dumps(data, ensure_ascii=False)


def streaminfo_callback(data):
    data.pop('event_raw')
    data['pywitch_id'] = random_string(64)
    events['streaminfo'] = json.dumps(data, ensure_ascii=False)


app = Flask('app')


@app.route('/<kind>')
def route_tmi(kind):
    if kind not in events:
        return '{}'
    return json.dumps(events[kind], ensure_ascii=False)


class PyWitchClientManager:
    def __init__(
        self,
        token=None,
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

        self.features = {}

        if self.port:
            self.server_url = f'{self.host}:{self.port}'
        else:
            self.server_url = self.host

        self.is_running = False

    def get_auth_url(self, auth_endpoint='authenticate'):
        self.auth_endpoint = auth_endpoint
        self.auth_state_length = 128
        self.auth_state = random_string(self.auth_state_length)
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
            self.validation, self.helix_headers = validate_token(
                token, verbose=False
            )
        except:
            self.validation = {}
        return self.validation

    def verify_channel(self, channel):
        return get_user_info(login=channel, helix_headers=self.helix_headers)

    def start_flask(self):
        kwargs = {
            'host': self.host,
            'port': self.port,
            'threaded': True,
            'use_reloader': False,
            'debug': False,
        }

        self.flask_thread = threading.Thread(
            target=app.run, daemon=True, kwargs=kwargs
        )
        self.flask_thread.start()

    def start_validator(self, token):
        self.is_running = True
        self.token = token
        self.validator_thread = threading.Thread(
            target=self.validator_task, args=(self.token,), daemon=True
        )
        self.validator_thread.start()

    def validator_task(self, token, interval=600):
        time.sleep(interval)
        num = 0
        while self.is_running:
            # The pourpose behind this is to avoid multiple instances of
            # validator running at the same time.
            num += 1
            time.sleep(1)
            if num >= interval:
                self.validate(token)

    def start_pywitch(self, channel, token, features):
        self.is_running = True
        self.token = token
        self.channel = channel
        if not self.channel:
            raise Exception("Missing channel!")
        if not self.token:
            raise Exception("Missing token!")
        if 'tmi' in features:
            self.features['tmi'] = PyWitchTMI(
                self.channel, self.token, tmi_callback
            )
        if 'heat' in features:
            self.features['heat'] = PyWitchHeat(
                self.channel, self.token, heat_callback
            )
        if 'redemptions' in features:
            self.features['redemptions'] = PyWitchRedemptions(
                self.token, redemptions_callback
            )
        if 'streaminfo' in features:
            self.features['streaminfo'] = PyWitchStreamInfo(
                self.channel, self.token, streaminfo_callback
            )

        for v in self.features.values():
            v.start()

    def stop_all(self):
        self.is_running = False
        for v in self.features.values():
            thread = threading.Thread(target=v.stop, args=(), daemon=True)
            thread.start()
            
    def get_version_in_repository(self):
        version_file_url = (
            'https://raw.githubusercontent.com/ouriquegustavo/'
            'pywitch_client/main/src/pywitch_client/_version.py'
        )
        response = requests.get(version_file_url)
        if response.status_code==200:
            return response.text.split("'")[1]
