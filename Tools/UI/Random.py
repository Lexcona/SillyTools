import os

import dearpygui.dearpygui as dpg

import ColorPallets.Catpuccin.Mocha
import Libs.Networking
import Tools.Backend.Random

import themes

import re
import uuid
import socket

import requests

from Vars.General import catagories

def json_formater():
    dpg.add_input_text(
        tag="random.json_formater_json_input",
        hint="URLs",
        multiline=True,
        width=480,
        height=185,
    )

        #dpg.add_spacer(width=8)

    dpg.add_button(
        label="Format JSON",
        callback=Tools.Backend.Random.json_formater,
        user_data=None,
        width=480,
    )

    dpg.add_spacer(height=12)

    themes.set_colored_result("random.json_formater_json_input", themes.default_result_text, "Mauve")

def computer_information():
    dpg.add_input_text(
        default_value="",
        tag="random.computer_information_result_text",
        multiline=True,
        width=480,
        height=240,
        readonly=True
    )

    themes.set_colored_result("random.computer_information_result_text", "getting computer information...", "Mauve")

    info_text = f"network\n"
    info_text += f"public ip: {requests.get('https://api.ipify.io').text}\n"
    info_text += f"private ip: {Libs.Networking.get_local_ip()}\n"
    info_text += f"mac address: {':'.join(re.findall('..', '%012x' % uuid.getnode()))}\n"
    info_text += f"\nuser\n"
    info_text += f"current user: {os.getlogin()}\n"

    themes.set_colored_result("random.computer_information_result_text", info_text, "Mauve")

def all_tools():
    dpg.add_input_text(
        default_value="",
        tag="random.all_tools",
        multiline=True,
        width=480,
        height=240,
        readonly=True
    )

    themes.set_colored_result("random.all_tools", "getting all the tools...", "Mauve")

    long_bar = "---------------------------------\n"

    info_text = f"Silly Tools toolset:\n\n"
    info_text += long_bar
    for key, value in catagories.items():
        info_text += f"{key}:\n"
        for tool in value['tools']:
            info_text += f" - {tool['name']}\n"
        info_text += long_bar

    themes.set_colored_result("random.all_tools", info_text, "Mauve")