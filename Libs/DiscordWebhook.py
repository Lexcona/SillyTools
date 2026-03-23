import base64

import requests

from rich.console import Console

console = Console()

def url_to_base64(img_url):
    img = requests.get(img_url).content
    return base64.b64encode(img).decode()

def get_info(url:str):
    res = requests.get(url)
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def send_message(url:str, message:str):
    data = {
        "content": message
    }
    res = requests.post(url, json=data)
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def modify_webhook(url:str, name:str=None, avatar:str=None, channel_id:int=None):
    data = {
        "name":name,
        "avatar": f"data:image/png;base64,{url_to_base64(avatar)}",
        "channel_id": channel_id
    }
    res = requests.patch(url, json=data)
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def delete_webhook(url:str):
    res = requests.delete(url)
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def get_message(url:str, message:int):
    res = requests.get(url+"/messages/"+str(message))
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def edit_message(url:str, message:int):
    data = {
        "content": message
    }
    res = requests.patch(url+"/messages/"+str(message), json=data)
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def delete_message(url:str, message:int):
    res = requests.delete(url+"/messages/"+str(message))
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()