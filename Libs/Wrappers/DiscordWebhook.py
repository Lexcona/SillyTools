import base64

import requests

import Libs.Networking

from Vars.General import console

def url_to_base64(img_url):
    img = requests.get(img_url, proxies=Libs.Networking.get_proxies()).content
    return base64.b64encode(img).decode()

def get_info(url:str):
    res = requests.get(url, proxies=Libs.Networking.get_proxies())
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def send_message(url:str, message:str):
    data = {
        "content": message
    }
    res = requests.post(url, json=data, proxies=Libs.Networking.get_proxies())
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
    res = requests.patch(url, json=data, proxies=Libs.Networking.get_proxies())
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def delete_webhook(url:str):
    res = requests.delete(url, proxies=Libs.Networking.get_proxies())
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def get_message(url:str, message:int):
    res = requests.get(url+"/messages/"+str(message), proxies=Libs.Networking.get_proxies())
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def edit_message(url:str, message:int):
    data = {
        "content": message
    }
    res = requests.patch(url+"/messages/"+str(message), json=data, proxies=Libs.Networking.get_proxies())
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()

def delete_message(url:str, message:int):
    res = requests.delete(url+"/messages/"+str(message), proxies=Libs.Networking.get_proxies())
    if res.status_code == 404:
        return False
    res.raise_for_status()
    return res.json()