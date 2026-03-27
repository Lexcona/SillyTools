import os

import dearpygui.dearpygui as dpg

import Libs.General
from ColorPallets.Catpuccin import Mocha

from Libs.ConfigManager import config

def button_callback(sender, app_data):
    print(f"Button pressed! Value: {app_data}")

dpg.create_context()

import themes

import Tools.UI.OSInt
import Tools.UI.Settings
import Tools.UI.Internet
import Tools.UI.Discord
import Tools.UI.GeneralInfo
import Tools.UI.Random

with dpg.font_registry():
    big_font = dpg.add_font("Fonts/Press_Start_2P/PressStart2P-Regular.ttf", 17)
    default_font = dpg.add_font("Fonts/determination-mono-web-font/DeterminationSansWebRegular-369X.ttf", 20)
    small_font = dpg.add_font("Fonts/determination-mono-web-font/DeterminationSansWebRegular-369X.ttf", 16)

dpg.bind_font(default_font)

selected_catagory = 0

title = "Silly Tools :3"

dpg.create_viewport(
    title=title,
    width=1335,
    height=720,
    resizable=False
)
dpg.set_viewport_small_icon("Assets/icon.png")

catagories = []

def add_catagory(name:str, cat_func):
    catagories.append({"name": name, "func": cat_func})

def set_catagory(sender, app_data, user_data):
    global selected_catagory
    selected_catagory = user_data

    if dpg.does_item_exist("content_area"):
        dpg.delete_item("content_area", children_only=True)

    if catagories:
        catagories[selected_catagory]["func"]()

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

def show_home():
    dpg.add_spacer(height=20, parent="content_area")
    dpg.add_text(
        f"""Welcome {os.getlogin()}, this is just a silly little tool to just to let me do silly things.
            Also to any federal agents looking at this...
            THIS TOOL SHOULD NOT BE USED AGAINST ANYTHING WITHOUT THE PERMISSION OF THE PERSON OR OWNER.
            I AM NOT RESPONSIBLE IF YOU USE IT ON ANYONE.
            Also cash if you are reading this, this is not evidence of me being a furry femboy.""".replace("  ", ""),
        wrap=0,
        parent="content_area"
    )

def show_osint():
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("GitHub Email Search", Tools.UI.OSInt.github_email_search, width=500, height=300, parent=hor_group)
        create_tool("IP Lookup", Tools.UI.OSInt.ip_lookup, width=500, height=300, parent=hor_group)
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("Username Search", Tools.UI.OSInt.username_search, width=500, height=300, parent=hor_group)

def show_settings():
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("API Keys", Tools.UI.Settings.api_keys, width=450, height=300, parent=hor_group)
        create_tool("Menu Settings", Tools.UI.Settings.menu_settings, width=450, height=300, parent=hor_group)

def show_internet():
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("Get Domain Nameservers", Tools.UI.Internet.find_name_servers, width=500, height=300, parent=hor_group)
        create_tool("Connected Domain Finder (Certs)", Tools.UI.Internet.find_cert_domains, width=500, height=300, parent=hor_group)
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("DNS Dump", Tools.UI.Internet.domain_to_ip, width=500, height=300, parent=hor_group)
        create_tool("Site Mapper", Tools.UI.Internet.site_mapper, width=500, height=300, parent=hor_group)
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("Tag Dumper", Tools.UI.Internet.tag_dumper, width=500, height=300, parent=hor_group)
        create_tool("Method Scanner", Tools.UI.Internet.method_scanner, width=500, height=300, parent=hor_group)
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("URL Checker", Tools.UI.Internet.url_checker, width=500, height=300, parent=hor_group)
        create_tool("Website Info", Tools.UI.Internet.website_info, width=500, height=300, parent=hor_group)
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("WHOIS Search", Tools.UI.Internet.whois_search, width=500, height=300, parent=hor_group)

def show_discord():
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("Discord Webhook Manager", Tools.UI.Discord.discord_webhook_manager, width=500, height=300, parent=hor_group)

def show_general_info():
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("Minecraft Lookup", Tools.UI.GeneralInfo.minecraft_lookup, width=500, height=300, parent=hor_group)

def show_random():
    with dpg.group(horizontal=True, parent="content_area") as hor_group:
        create_tool("JSON Formater", Tools.UI.Random.json_formater, width=500, height=300, parent=hor_group)
        create_tool("Computer Information", Tools.UI.Random.computer_information, width=500, height=300, parent=hor_group)


add_catagory("Home", show_home)
add_catagory("OSInt", show_osint)
add_catagory("Internet", show_internet)
add_catagory("General Info", show_general_info)
add_catagory("Random", show_random)
#add_catagory("Discord", show_discord)
add_catagory("Settings", show_settings)


with dpg.window(label="Main Content", tag="main_window", no_title_bar=True, no_resize=True, no_move=True, no_close=True, no_collapse=True, no_background=False):
    with dpg.group(horizontal=True, tag="main_content_group"):
        with dpg.child_window(width=280, height=0, border=True, no_scrollbar=False):
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=-1)
                title_item = dpg.add_text(title)
                dpg.add_spacer(width=-1)

            dpg.bind_item_font(title_item, big_font)

            dpg.add_spacer(height=10)

            for i, cat in enumerate(catagories):
                dpg.add_button(label=cat["name"], height=30, width=-1, callback=set_catagory, user_data=i)
                dpg.add_separator()

        with dpg.child_window(width=0, height=0, border=True, no_scrollbar=False, tag="content_area"):
            pass

themes.current_theme = themes.theme_dict[config.read("theme", list(themes.theme_dict.keys())[0])]
dpg.bind_theme(themes.current_theme["theme"])

#dpg.show_item_registry()

set_catagory(None, None, 0)

dpg.setup_dearpygui()
dpg.set_primary_window("main_window", True)
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()