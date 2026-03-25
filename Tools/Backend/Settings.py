import dearpygui.dearpygui as dpg

import os
import json

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