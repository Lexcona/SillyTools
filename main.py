import os

import dearpygui.dearpygui as dpg

import Libs.General
from ColorPallets.Catpuccin import Mocha

from Libs.ConfigManager import config

dpg.create_context()

import themes

import Tools.UI.OSInt
import Tools.UI.Settings
import Tools.UI.Internet
import Tools.UI.Discord
import Tools.UI.GeneralInfo
import Tools.UI.Random

from rich.console import Console

console = Console()

with dpg.font_registry():
    big_font = dpg.add_font(Libs.General.resource_path("Fonts/Press_Start_2P/PressStart2P-Regular.ttf"), 17)
    default_font = dpg.add_font(Libs.General.resource_path("Fonts/determination-mono-web-font/DeterminationSansWebRegular-369X.ttf"), 20)
    small_font = dpg.add_font(Libs.General.resource_path("Fonts/determination-mono-web-font/DeterminationSansWebRegular-369X.ttf"), 16)

dpg.bind_font(default_font)

selected_catagory = ""

title = "Silly Tools :3"

dpg.create_viewport(
    title=title,
    width=1335,
    height=720,
    resizable=False
)
dpg.set_viewport_small_icon(Libs.General.resource_path("Assets/icon.png"))

catagories = {}

def add_catagory(name:str, thing:str=""):
    catagories[name] = {"tools": [], "text": thing}

def add_tool(name:str, tool:object, cat:str):
    if cat in list(catagories.keys()):
        catagories[cat]["tools"].append({"name": name, "tool": tool})
    else:
        console.print(f"cat no found :( {cat}", style="red")

def set_catagory(sender, app_data, user_data):
    global selected_category
    selected_category = user_data

    if dpg.does_item_exist("content_area"):
        dpg.delete_item("content_area", children_only=True)

    if not selected_category or selected_category not in catagories:
        return

    tools = catagories[selected_category]["tools"]

    for i in range(0, len(tools), 2):
        with dpg.group(horizontal=True, parent="content_area") as hor_group:
            tool1 = tools[i]
            create_tool(tool1["name"], tool1["tool"], width=500, height=300, parent=hor_group)

            if i + 1 < len(tools):
                tool2 = tools[i + 1]
                create_tool(tool2["name"], tool2["tool"], width=500, height=300, parent=hor_group)


def create_tool(name: str, build_ui_func, width=450, height=300, parent=None):
    with dpg.child_window(
        width=int(width),
        height=int(height),
        border=True,
        parent=parent,
        no_scrollbar=False,
    ):
        with dpg.group(horizontal=True):
            dpg.add_text(name, color=themes.current_theme["pallet"].Rosewater)
            dpg.add_spacer(width=-1)
        dpg.add_separator()
        build_ui_func()

welcome_text = f"""Welcome {Libs.General.get_user_full_name()}, this is just a silly little tool to just to let me do silly things :3.
Also to any federal agents looking at this...
THIS TOOL SHOULD NOT BE USED AGAINST ANYTHING WITHOUT THE PERMISSION OF THE PERSON OR OWNER.
I AM NOT RESPONSIBLE IF YOU USE IT ON ANYONE.""".replace("  ", "")

add_catagory("Home", welcome_text)
add_catagory("OSInt")
add_catagory("Internet")
add_catagory("General Info")
add_catagory("Random")
#add_catagory("Discord", show_discord)
add_catagory("Settings")

# OSInt Stuff
add_tool("GitHub Email Search", Tools.UI.OSInt.github_email_search, "OSInt")
add_tool("IP Lookup", Tools.UI.OSInt.ip_lookup, "OSInt")
add_tool("Username Search", Tools.UI.OSInt.username_search, "OSInt")

# Internet Stuff
add_tool("Get Domain Nameservers", Tools.UI.Internet.find_name_servers, "Internet")
add_tool("Connected Domain Finder (Certs)", Tools.UI.Internet.find_cert_domains, "Internet")
add_tool("DNS Dump", Tools.UI.Internet.domain_to_ip, "Internet")
add_tool("Site Mapper", Tools.UI.Internet.site_mapper, "Internet")
add_tool("Tag Dumper", Tools.UI.Internet.tag_dumper, "Internet")
add_tool("Method Scanner", Tools.UI.Internet.method_scanner, "Internet")
add_tool("URL Checker", Tools.UI.Internet.url_checker, "Internet")
add_tool("Website Info", Tools.UI.Internet.website_info, "Internet")
add_tool("WHOIS Search", Tools.UI.Internet.whois_search, "Internet")
add_tool("Email Scrapper", Tools.UI.Internet.email_scrapper, "Internet")

# General Info
add_tool("Minecraft Lookup", Tools.UI.GeneralInfo.minecraft_lookup, "General Info")

# General Info
add_tool("JSON Formater", Tools.UI.Random.json_formater, "Random")

# Discord Stuff
add_tool("Discord Webhook Manager", Tools.UI.Discord.discord_webhook_manager, "Discord")

with dpg.window(label="Main Content", tag="main_window", no_title_bar=True, no_resize=True, no_move=True, no_close=True, no_collapse=True, no_background=False):
    with dpg.group(horizontal=True, tag="main_content_group"):
        with dpg.child_window(width=280, height=0, border=True, no_scrollbar=False):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=-1)
                title_item = dpg.add_text(title)
                dpg.add_spacer(width=-1)

            dpg.bind_item_font(title_item, big_font)

            dpg.add_spacer(height=10)

            for cat_name in catagories.keys():
                dpg.add_button(label=cat_name, height=30, width=-1, callback=set_catagory, user_data=cat_name)
                dpg.add_separator()

        with dpg.child_window(width=0, height=0, border=True, no_scrollbar=False, tag="content_area"):
            pass

themes.current_theme = themes.theme_dict[config.read("theme", list(themes.theme_dict.keys())[0])]
dpg.bind_theme(themes.current_theme["theme"])

#dpg.show_item_registry()

set_catagory(None, None, list(catagories.keys())[0])

dpg.setup_dearpygui()
dpg.set_primary_window("main_window", True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()