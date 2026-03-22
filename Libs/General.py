import os

from Libs.ConfigManager import ConfigManager

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