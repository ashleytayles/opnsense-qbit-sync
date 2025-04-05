import os
import requests
import json
from typing import Dict, Optional
from dataclasses import dataclass
import urllib3

urllib3.disable_warnings()

class QBittorrent:
    def __init__(self, host: str, port: int, user: str, password: str, ssl: bool, ssl_verify: bool):
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
        if self._listen_port == None:
            if self.auth_cookie == None:
                self.login()
            settings_response = self.session.get(f"{self.url}/api/v2/app/preferences")
            settings_response.raise_for_status()
            self._listen_port = settings_response.json()['listen_port']
        return self._listen_port
    
    @listen_port.setter
    def listen_port(self, new_port: int):
        """ Method to set current listen_port setting in  qBittorrent """
        if self.listen_port != new_port:
            if self.auth_cookie == None:
                self.login()
            qbit_settings_body: dict = {"listen_port": new_port}
            qbit_settings_response = self.session.post(f"{self.url}/api/v2/app/setPreferences", data={"json": json.dumps(qbit_settings_body)})
            qbit_settings_response.raise_for_status()

class OPNSense:
    def __init__(self, host: str, port: int, api_key: str, api_secret: str, ssl: bool, ssl_verify: bool):
        self.host: str = host
        self.port: int = port
        self.api_key: str = api_key
        self.api_secret: str = api_secret
        self.ssl: bool = ssl_verify
        self.session: requests.Session = requests.Session()
        self.session.auth = (api_key, api_secret)
        self.session.verify = False
        self.schema: str = "https://" if ssl else "http://"
        self.url: str = f"{self.schema}{self.host}:{self.port}"
        
@dataclass
class FirewallAlias:
    name: str
    device: OPNSense
    _alias_type: Optional[str] = None
    _uuid: Optional[str] = None
    _content: Optional[str] = None
    _cache: Optional[dict] = None

    @property
    def uuid(self) -> str:
        if self._uuid == None:
            all_aliases_response = self.device.session.get(f"{self.device.url}/api/firewall/alias/get")
            all_aliases_response.raise_for_status()
            all_aliases: dict = all_aliases_response.json()['alias']['aliases']['alias']
            for alias, alias_data in all_aliases.items():
                if alias_data['name'] == O_FORWARDED_PORT_ALIAS:
                    self._uuid = alias
                    self._cache = alias_data
        return self._uuid

    @property
    def alias_type(self) -> str:
        if self._alias_type == None:
            if self._cache == None:
                alias_request = self.device.session.get(f"{self.device.url}/api/firewall/alias/getItem/{self.uuid}")
                alias_request.raise_for_status()
                alias_type_dict: dict = alias_request.json()['alias']['type']
            else:
                alias_type_dict: dict = self._cache['type']
            for alias_type, type_data in alias_type_dict.items():
                if type_data['selected'] == 1:
                    self._alias_type = alias_type
        return self._alias_type
    
    @property
    def content(self):
        if self._content == None:
            if self._cache == None:
                alias_request = self.device.session.get(f"{self.device.url}/api/firewall/alias/getItem/{self.uuid}")
                alias_request.raise_for_status()
                alias_content_dict: dict = alias_request.json()['alias']['content']
            else:
                alias_content_dict: dict = self._cache['content']
            for alias_content in alias_content_dict.values():
                if alias_content['selected'] == 1:
                    self._content = alias_content['value']
        return self._content
                    
        


def main():

    qbit = QBittorrent(Q_HOST, Q_PORT, Q_USER, Q_PASS, Q_SSL, Q_SSL_VERIFY)
    opnsense: OPNSense = OPNSense(O_HOST, O_PORT, O_API_KEY, O_API_SECRET, O_SSL, O_SSL_VERIFY)
    source_alias: FirewallAlias = FirewallAlias(O_FORWARDED_PORT_ALIAS, opnsense)


    if qbit.listen_port != int(source_alias.content):
        qbit.listen_port = int(source_alias.content)
        print(f"Updated qBit to listen on: {int(source_alias.content)}")
    else:
        print(f"qBit is already listening on {int(source_alias.content)}")

if __name__ == "__main__":

    Q_USER: str = os.getenv("Q_USER")
    Q_PASS: str = os.getenv("Q_PASS")
    Q_HOST: str = os.getenv("Q_HOST")
    Q_PORT: int = os.getenv("Q_PORT", 443)
    Q_SSL: bool = os.getenv("Q_SSL", True)
    Q_SSL_VERIFY: bool = os.getenv("Q_SSL", True)

    O_HOST: str = os.getenv("O_HOST")
    O_PORT: str = os.getenv("O_PORT", 8443)
    O_API_KEY: str = os.getenv("O_API_KEY")
    O_API_SECRET: str = os.getenv("O_API_SECRET")
    O_FORWARDED_PORT_ALIAS: str = os.getenv("O_FORWARDED_PORT_ALIAS")
    O_SSL: bool = os.getenv("O_SSL")
    O_SSL_VERIFY: bool = os.getenv("O_SSL_VERIFY")
    
    main()