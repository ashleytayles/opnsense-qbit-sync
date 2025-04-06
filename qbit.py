""" Classes and functions for interacting with qBittorrent """

from typing import Optional, Dict
import json
import requests

class QBittorrent:
    """ Defines a qBittorrent instance and provides methods to interact with it """

    def __init__(self, host: str, port: int, user: str, password: str, ssl: bool, ssl_verify: bool = True):
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.session: requests.Session = requests.Session()
        self.session.auth = (user, password)
        self.auth_cookie: Optional[Dict[str, str]] = None
        self.session.headers = {'Referer': f'https://{host}:{port}'}
        self._listen_port: Optional[int] = None
        self.ssl: bool = ssl
        self.session.verify = ssl_verify
        self.schema: str = "https://" if ssl else "http://"
        self.url: str = f"{self.schema}{self.host}:{self.port}"

    def login(self) -> None:
        """Use login endpoint to set auth cookie"""

        qbit_login = {'username': self.user,'password': self.password}

        qbit_login_response = self.session.post(f"{self.url}/api/v2/auth/login", data=qbit_login)
        qbit_login_response.raise_for_status()

        self.session.cookies = qbit_login_response.cookies

    @property
    def listen_port(self):
        """ Method to get current listen_port setting from qBittorrent """
        if self._listen_port is None:
            if self.auth_cookie is None:
                self.login()
            settings_response = self.session.get(f"{self.url}/api/v2/app/preferences")
            settings_response.raise_for_status()
            self._listen_port = settings_response.json()['listen_port']
        return self._listen_port

    @listen_port.setter
    def listen_port(self, new_port: int):
        """ Method to set current listen_port setting in  qBittorrent """
        if self.listen_port != new_port:
            if self.auth_cookie is None:
                self.login()
            qbit_settings_body: dict = {"listen_port": new_port}
            qbit_settings_response = self.session.post(f"{self.url}/api/v2/app/setPreferences", data={"json": json.dumps(qbit_settings_body)})
            qbit_settings_response.raise_for_status()
