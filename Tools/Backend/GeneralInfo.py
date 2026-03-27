import requests

import dearpygui.dearpygui as dpg

import themes
from Libs.Wrappers import Mojang

def minecraft_lookup():
    result_text = "generalInfo.minecraft_lookup_result_text"

    username = dpg.get_value("generalInfo.minecraft_lookup_username_input").strip()

    if not username:
        themes.set_colored_result(result_text, "you kinda forgot the username...", "Red")
        return

    user_data = Mojang.get_skin_data(username)

    if user_data == "Not Found":
        themes.set_colored_result(result_text, "user no found :(", "Red")
        return

    info_text = "found things :3\n\n"

    info_text += f"username: {user_data['name']}\n"
    info_text += f"id: {user_data['id']}\n"
    info_text += f"skin: {user_data['textures']['textures'].get('SKIN', {}).get('url', 'not found')}\n"
    info_text += f"cape: {user_data['textures']['textures'].get('CAPE', {}).get('url', 'not found')}\n"

    themes.set_colored_result(result_text, info_text, "Mauve")