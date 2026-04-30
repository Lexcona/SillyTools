import os
import ctypes
import platform

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


def get_user_full_name():
    system = platform.system()

    if system == "Windows":
        GetUserNameExW = ctypes.windll.secur32.GetUserNameExW
        NameDisplay = 3

        size = ctypes.pointer(ctypes.c_ulong(0))
        GetUserNameExW(NameDisplay, None, size)
        name_buffer = ctypes.create_unicode_buffer(size.contents.value)
        GetUserNameExW(NameDisplay, name_buffer, size)
        return name_buffer.value.strip()

    else:
        import pwd
        try:
            pw_entry = pwd.getpwuid(os.geteuid())
            full_name = pw_entry.pw_gecos.split(',')[0].strip()
            if full_name:
                return full_name
            return pw_entry.pw_name
        except (ImportError, KeyError, IndexError):
            return os.environ.get('USER') or os.environ.get('USERNAME') or "Unknown User"

def replace_placeholders(text:str, vars:dict):
    for key, value in vars.items():
        text = text.replace("["+key+"]", value)
    return text

def dir_callback(sender, app_data, user_data):
    dpg.set_value(user_data, app_data["file_path_name"])

import sys
import os

# pyinstaller makes dpg go stupid
def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)