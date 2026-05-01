import os
import sys
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

# pyinstaller makes dpg go stupid
def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# done with gpt since I couldn't find out why the serializer didn't want to work.
def auto_serialize(obj):
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, bytes):
        return obj.hex()
    if isinstance(obj, (list, tuple, set)):
        return [auto_serialize(item) for item in obj]
    if isinstance(obj, dict):
        return {k: auto_serialize(v) for k, v in obj.items()}

    if hasattr(obj, "__dict__") and not isinstance(obj, type):
        clean = {
            key: auto_serialize(value)
            for key, value in obj.__dict__.items()
            if not key.startswith("_") and value is not None
        }
        if clean:
            return clean

    return str(obj)

# this part not though
def dict_to_pretty_str(data:(dict, list), indent:int=0, better_looking:bool=False):
    data = auto_serialize(data)

    lines = []
    spacing = "    " * indent

    if isinstance(data, dict):
        for key, value in data.items():
            if better_looking:
                key = key.upper().replace("_", " ").replace("-", " ")

            if isinstance(value, (dict, list)):
                lines.append(f"{spacing}{key}:")
                lines.append(dict_to_pretty_str(value, indent + 1, better_looking))
            else:
                lines.append(f"{spacing}{key}: {value}")

    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{spacing}-")
                lines.append(dict_to_pretty_str(item, indent + 1, better_looking))
            else:
                lines.append(f"{spacing}- {item}")

    else:
        lines.append(f"{spacing}{data}")

    return "\n".join(lines)