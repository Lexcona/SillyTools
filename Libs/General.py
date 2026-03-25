import os

from Libs.ConfigManager import ConfigManager
import dearpygui.dearpygui as dpg

config = ConfigManager()

def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def color_fixer(color:list):
    cool = []
    for i in color:
        cool.append(i/255)
    return cool


def replace_placeholders(text:str, vars:dict):
    for key, value in vars.items():
        text = text.replace("["+key+"]", value)
    return text

def dir_callback(sender, app_data, user_data):
    dpg.set_value(user_data, app_data["file_path_name"])