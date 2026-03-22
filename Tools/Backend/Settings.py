import dearpygui.dearpygui as dpg

import os
import json

from Libs.ConfigManager import config

def github_api_key():
    config.write("api_keys/github", dpg.get_value("github_api_key").strip())

def ipinfo_api_key():
    config.write("api_keys/ipinfo", dpg.get_value("ipinfo_api_key").strip())