# PyWitch Client

![pywitch_logo](logo/pywitch_logo.png)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

PyWitch Client is a GUI interface to PyWitch library combined with a Web
Application Framework (Flask).

Its main purpose is to provide HTTP endpoint to get the lastest Twitch events
captured with PyWitch.

The functionalities included are: 

* Automatic token generation (server side)

* Token validation;

* StreamInfo endpoint (real time stream information);

* TMI endpoint (twitch Messaging Interface);

* Redemptions endpoint (chat redemptions and rewards);

* Heat endpoint (heat extension).

## Requirements ##
```
Flask==2.0.2
PyQt5==5.15.6
PyQt5-Qt5==5.15.2
PyQt5-sip==12.9.0
pywitch==1.0.2
requests==2.26.0
websocket-client==1.2.1
```

## How to execute ##
To use it, you can run in `src/pywitch_client` folder:
```
python app.py
```

Or, if you are using Windows OS, double click the executable file, that can be
downloaded in the releases section.

The executable binaries where made with `pyinstaller`.

### I STRONGLY RECOMENDS TO RUN FROM SOURCE INSTEAD OF THE EXECUTABLE ###

## Generating tokens ##

To generate tokens, you just need to click Start PyWitch button. It will open
a browser page asking for authorization, and, after that, your token will be
generated in server, allowing you to recover it using a request later.

This procedure is automatic, you just need to wait and after some seconds
you will have your token.

Since the token generation is server side, here are some details:

* The server will store your token for a maximum of 120 seconds. If your
PyWitch Client was not able to recover in this interval, it will be destroyed.

* If your token was destroyed, just try to get another one following the same
procedure as before!

* After a successful attempt of token recovery, your token will be destroyed
in the server, avoiding any kind of token stealing.

* To recover your token from server, you need an unique random key of 128
characters, avoiding any kind of token stealing (again!).

* The server will store your Twitch `user_id` and `display_name`. These
information are public and the main purpose of keeping this information is to
share your livestream with other users!

* After your token been recovered by PyWitch Client, it will be stored in
this file: `pywitch_client_config.ini`.

* If you don't feel confortable of using an automatic token generation service
, you can generate your tokens manually and filling the configuration file
with them.

## Getting event data ##

After executing PyWitch Client and starting it, it will provide the event data
in localhost endpoints. You can change the host and port by editing the
configuration file.

The default endpoints are:
```
127.0.0.1:13486/tmi
127.0.0.1:13486/heat
127.0.0.1:13486/streaminfo
127.0.0.1:13486/redemptions
```

Event data will be in a JSON object, which updates in real time if the feature
box is checked before the PyWitch Client start.


