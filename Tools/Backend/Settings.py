import dearpygui.dearpygui as dpg

import os
import json
import urllib.parse

import themes

from Libs.ConfigManager import config

def github_api_key():
    config.write("api_keys/github", dpg.get_value("github_api_key").strip())

def ipinfo_api_key():
    config.write("api_keys/ipinfo", dpg.get_value("ipinfo_api_key").strip())

def set_theme():
    selected_theme = dpg.get_value("menu_settings.theme").strip()
    config.write("theme", selected_theme)
    themes.current_theme = themes.theme_dict[selected_theme]
    dpg.bind_theme(themes.current_theme["theme"])

def set_http_proxy():
    #print("http")
    url = dpg.get_value("menu_settings.http_proxy_input").strip()
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "http://" + url
    elif parsed.scheme != "http":
        url = url.replace(parsed.scheme, "http")

    config.write("proxies/http", url.strip())

def set_https_proxy():
    #print("https")
    url = dpg.get_value("menu_settings.https_proxy_input").strip()
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
    elif parsed.scheme != "https":
        url = url.replace(parsed.scheme, "https")

    config.write("proxies/https", url.strip())

def set_socks5_proxy():
    #print("socks5")
    url = dpg.get_value("menu_settings.socks5_proxy_input").strip()
    parsed = urllib.parse.urlparse(url)
    if not parsed.scheme:
        url = "socks5://" + url
    elif parsed.scheme != "socks5":
        url = url.replace(parsed.scheme, "socks5")

    config.write("proxies/socks5", url.strip())