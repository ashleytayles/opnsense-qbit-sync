import os
import requests
import json

O_HOST: str = os.getenv("O_HOST")
O_PORT: str = os.getenv("O_PORT", 8443)
O_API_KEY: str = os.getenv("O_API_KEY")
O_API_SECRET: str = os.getenv("O_API_SECRET")
O_FORWARDED_PORT_ALIAS: str = os.getenv("O_FORWARDED_PORT_ALIAS")

Q_USER: str = os.getenv("Q_USER")
Q_PASS: str = os.getenv("Q_PASS")
Q_HOST: str = os.getenv("Q_HOST")

DISCOVERED_PORT: int = 0

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


qbit_session: requests.Session = requests.Session()
qbit_session.auth = (Q_USER, Q_PASS)

qbit_login = {
    'username': Q_USER,
    'password': Q_PASS
}

qbit_headers = {
    'Referer': f"https://{Q_HOST}"
}

qbit_login_response = qbit_session.post(f"https://{Q_HOST}/api/v2/auth/login", data= qbit_login, headers= qbit_headers)

cookie = {
    'SID': qbit_login_response.cookies['SID']
}


qbit_settings_body: dict = {"listen_port": DISCOVERED_PORT}

qbit_settings_response = qbit_session.post(f"https://{Q_HOST}/api/v2/app/setPreferences", data={"json": json.dumps(qbit_settings_body)}, cookies=cookie)
qbit_settings_response.raise_for_status()

print(f"Updated qBit to listen on: {DISCOVERED_PORT}")

