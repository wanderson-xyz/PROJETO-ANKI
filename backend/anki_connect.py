import requests

URL = "http://localhost:8765"

def anki_connect(action, params=None):

    if params is None:
        params = {}

    payload = {
        "action": action,
        "version": 6,
        "params": params
    }

    response = requests.post(URL, json=payload)

    return response.json()["result"]