import os
import requests
import json
from typing import Dict, Optional

O_HOST: str = os.getenv("O_HOST")
O_PORT: str = os.getenv("O_PORT", 8443)
O_API_KEY: str = os.getenv("O_API_KEY")
O_API_SECRET: str = os.getenv("O_API_SECRET")
O_FORWARDED_PORT_ALIAS: str = os.getenv("O_FORWARDED_PORT_ALIAS")

Q_USER: str = os.getenv("Q_USER")
Q_PASS: str = os.getenv("Q_PASS")
Q_HOST: str = os.getenv("Q_HOST")
Q_PORT: int = os.getenv("Q_PORT", 443)

DISCOVERED_PORT: int = 0

class QBittorrent:
    def __init__(self, host: str, port: int, user: str, password: str):
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.session: requests.Session = requests.Session()
        self.session.auth = (user, password)
        self.auth_cookie: Optional[Dict[str, str]] = None
        self.session.headers = {'Referer': f'https://{host}:{port}'}
        self._listen_port: Optional[int] = None
    
    def login(self) -> None:
        """Use login endpoint to set auth cookie"""

        qbit_login = {
            'username': self.user,
            'password': self.password
        }

        qbit_login_response = self.session.post(f"https://{self.host}/api/v2/auth/login", data=qbit_login)
        qbit_login_response.raise_for_status()

        self.session.cookies = qbit_login_response.cookies

    @property
    def listen_port(self):
        if self._listen_port == None:
            if self.auth_cookie == None:
                self.login()
            settings_response = self.session.get(f"https://{self.host}/api/v2/app/preferences")
            settings_response.raise_for_status()
            self._listen_port = settings_response.json()['listen_port']
        return self._listen_port
    
    @listen_port.setter
    def listen_port(self, new_port: int):
        if self.listen_port != new_port:
            if self.auth_cookie == None:
                self.login()
            qbit_settings_body: dict = {"listen_port": DISCOVERED_PORT}
            qbit_settings_response = self.session.post(f"https://{Q_HOST}/api/v2/app/setPreferences", data={"json": json.dumps(qbit_settings_body)})
            qbit_settings_response.raise_for_status()

opnsense_session: requests.Session = requests.Session()
opnsense_session.auth = (O_API_KEY, O_API_SECRET)
opnsense_session.verify = False

all_aliases_response = opnsense_session.get(f"https://{O_HOST}:{O_PORT}/api/firewall/alias/get")
all_aliases_response.raise_for_status()

all_aliases: list = all_aliases_response.json()['alias']['aliases']['alias'].values()

for alias in all_aliases:
    if alias['name'] == O_FORWARDED_PORT_ALIAS:
        DISCOVERED_PORT = int(list(alias['content'].keys())[0])
        
print(f"Discovered port: {DISCOVERED_PORT}")

qbit = QBittorrent(Q_HOST, Q_PORT, Q_USER, Q_PASS)

if qbit.listen_port != DISCOVERED_PORT:
    qbit.listen_port = DISCOVERED_PORT
    print(f"Updated qBit to listen on: {DISCOVERED_PORT}")
else:
    print(f"qBit is already listening on {DISCOVERED_PORT}")

