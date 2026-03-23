import json

import dearpygui.dearpygui as dpg

import ColorPallets.Catpuccin.Mocha
import Libs.General

import themes

def json_formater():
    result_text = "random.json_formater_json_input"

    json_data = dpg.get_value("random.json_formater_json_input").strip()

    if not json_data:
        themes.set_colored_result(result_text, "you kinda forgot the json data...", "Red")
        return

    try:
        data = json.loads(json_data)
    except Exception:
        themes.set_colored_result(result_text, f"{json_data}\nno real json :(", "Red")
        return

    themes.set_colored_result(result_text, json.dumps(data, indent=4), "Mauve")