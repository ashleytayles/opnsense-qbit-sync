""" This module syncs the content of an OPNSense 'port' type alias
    to the qBittorrent 'listen_port' parameter """

import os
import json
from dataclasses import dataclass
import urllib3
from qbit import QBittorrent
from opnsense import OPNSense, FirewallAlias, get_alias_from_name

urllib3.disable_warnings()

@dataclass
class OPNSenseQbitSyncSettings:
    Q_USER: str
    Q_PASS: str
    Q_HOST: str
    O_HOST: str
    O_PORT: str
    O_API_KEY: str
    O_API_SECRET: str
    O_FORWARDED_PORT_ALIAS: str
    Q_PORT: int = 443
    Q_SSL: bool = True
    Q_SSL_VERIFY: bool = True
    O_SSL: bool = True
    O_SSL_VERIFY: bool = True


def main():

    config: dict = get_settings()
    settings: OPNSenseQbitSyncSettings = OPNSenseQbitSyncSettings(**config)
    qbit = QBittorrent(settings.Q_HOST,
                       settings.Q_PORT,
                       settings.Q_USER,
                       settings.Q_PASS,
                       settings.Q_SSL,
                       ssl_verify=settings.Q_SSL_VERIFY)

    opnsense: OPNSense = OPNSense(settings.O_HOST,
                                  settings.O_PORT,
                                  settings.O_API_KEY,
                                  settings.O_API_SECRET,
                                  settings.O_SSL,
                                  ssl_verify=settings.O_SSL_VERIFY)

    source_alias: FirewallAlias = get_alias_from_name(opnsense,
                                                      settings.O_FORWARDED_PORT_ALIAS)


    if qbit.listen_port != int(source_alias.content):
        qbit.listen_port = int(source_alias.content)
        print(f"Updated qBit to listen on: {int(source_alias.content)}")
    else:
        print(f"qBit is already listening on {int(source_alias.content)}")

def get_settings() -> dict:
    """ Determine how this module is being configured and set variables """

    settings_file: str = "settings.json"

    if os.path.exists(settings_file):
        with open(settings_file, 'r', encoding='utf-8') as file:
            loaded_config: dict = json.load(file)
        return loaded_config
    else:
        config: dict = {}
        config["Q_USER"] = os.getenv("Q_USER")
        config["Q_PASS"] = os.getenv("Q_PASS")
        config["Q_HOST"] = os.getenv("Q_HOST")
        config["Q_PORT"] = int(os.getenv("Q_PORT", "443"))
        config["Q_SSL"] = os.getenv("Q_SSL", "True").lower() == "true"
        config["Q_SSL_VERIFY"] = os.getenv("Q_SSL_VERIFY", "True").lower() == "true"
        config["O_HOST"] = os.getenv("O_HOST")
        config["O_PORT"] = int(os.getenv("O_PORT", "8443"))
        config["O_API_KEY"] = os.getenv("O_API_KEY")
        config["O_API_SECRET"] = os.getenv("O_API_SECRET")
        config["O_FORWARDED_PORT_ALIAS"] = os.getenv("O_FORWARDED_PORT_ALIAS")
        config["O_SSL"] = os.getenv("O_SSL", "True").lower() == "true"
        config["O_SSL_VERIFY"] = os.getenv("O_SSL_VERIFY", "True").lower() == "true"
        return config

if __name__ == "__main__":
    main()
