import json
import base64

import requests


def get_uuid(username:str):
    res = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if res.status_code == 404:
        return "Not Found"
    res.raise_for_status()

    return res.json()["id"]

def get_skin_data(username:str):
    id = get_uuid(username)
    if id == "Not Found":
        return "Not Found"
    res = requests.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{id}?unsigned=false")
    res.raise_for_status()

    reconstructed_json = {}

    for key, value in res.json().items():
        if key.lower() != "properties":
            reconstructed_json[key] = value

    for data in res.json()["properties"]:
        reconstructed_json[data["name"]] = json.loads(base64.b64decode(data["value"].encode()).decode().strip())

    return reconstructed_json