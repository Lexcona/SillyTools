import json

import dearpygui.dearpygui as dpg

import ColorPallets.Catpuccin.Mocha
import Tools.Backend.Settings

from Libs.ConfigManager import config

show_keys = False

api_key_inputs = []

def toggle_keys():
    global show_keys
    if show_keys:
        for api_key_input in api_key_inputs:
            dpg.configure_item(api_key_input, password=True)
        show_keys = False
    else:
        for api_key_input in api_key_inputs:
            dpg.configure_item(api_key_input, password=False)
        show_keys = True

def api_keys():
    # GitHub API Key Set
    dpg.add_text(
        default_value="GitHub API Key",
        color=ColorPallets.Catpuccin.Mocha.Mauve,
        wrap=0
    )
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="github_api_key",
            hint="API Key",
            width=300,
            password=True
        )
        dpg.configure_item("github_api_key", default_value=config.read("api_keys/github", ""))

        dpg.add_spacer(width=8)

        dpg.add_button(
            label="Set API Key",
            callback=Tools.Backend.Settings.github_api_key,
            user_data=None
        )

        api_key_inputs.append("github_api_key")

    dpg.add_text(
        default_value="ipinfo.io API Key",
        color=ColorPallets.Catpuccin.Mocha.Mauve,
        wrap=0
    )
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="ipinfo_api_key",
            hint="API Key",
            width=300,
            password=True
        )
        dpg.configure_item("ipinfo_api_key", default_value=config.read("api_keys/ipinfo", ""))

        dpg.add_spacer(width=8)

        dpg.add_button(
            label="Set API Key",
            callback=Tools.Backend.Settings.ipinfo_api_key,
            user_data=None
        )

        api_key_inputs.append("ipinfo_api_key")

    dpg.add_button(
        label="Show/Hide Keys",
        callback=toggle_keys,
        user_data=None
    )