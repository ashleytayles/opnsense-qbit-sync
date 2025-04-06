""" Classes and functions for interacting with OPNSense """

from dataclasses import dataclass
from typing import Optional
import requests

class OPNSense:
    """ Defines an OPNSense instance and provides methods to interact with it """
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
    """ Defines an OPNSense firewall alias instance and provides methods to interact with it """
    name: str
    device: OPNSense
    uuid: str
    _alias_type: Optional[str] = None
    _content: Optional[str] = None
    _cache: Optional[dict] = None

    @property
    def alias_type(self) -> str:
        if self._alias_type is None:
            if self._cache is None:
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
        if self._content is None:
            if self._cache is None:
                alias_request = self.device.session.get(f"{self.device.url}/api/firewall/alias/getItem/{self.uuid}")
                alias_request.raise_for_status()
                alias_content_dict: dict = alias_request.json()['alias']['content']
            else:
                alias_content_dict: dict = self._cache['content']
            for alias_content in alias_content_dict.values():
                if alias_content['selected'] == 1:
                    self._content = alias_content['value']
        return self._content

def get_alias_from_name(device: OPNSense, name: str) -> FirewallAlias | None:
    all_aliases_response = device.session.get(f"{device.url}/api/firewall/alias/get")
    all_aliases_response.raise_for_status()
    all_aliases: dict = all_aliases_response.json()['alias']['aliases']['alias']
    for alias, alias_data in all_aliases.items():
        if alias_data['name'] == name:
            return FirewallAlias(name=name, uuid=alias, device=device)
    raise ValueError(f"No alias with name {name} was found on {device.host}")