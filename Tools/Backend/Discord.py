import dearpygui.dearpygui as dpg

import themes

from Libs.Wrappers import DiscordWebhook

from rich.console import Console

console = Console()

def get_webhook_info():
    result_thing = "discord.discord_webhook_manager_result_text"
    url = dpg.get_value("discord.discord_webhook_manager_url_input").strip()
    if not url:
        themes.set_colored_result(result_thing, "you kinda forgot the url...", "Red")
        return

    themes.set_colored_result(result_thing, "getting info...", "Mauve")
    try:
        web_info = DiscordWebhook.get_info(url)
        if web_info:
            info_text = "got webhook info :3\n"
            info_text += "Name: " + web_info.get("name", "Not Available")+"\n"
            info_text += "Avatar: " + web_info.get("avatar", "Not Available") + "\n"
            info_text += "Webhook ID: " + web_info.get("id", "Not Available")+"\n"
            info_text += "Channel ID: " + web_info.get("channel_id", "Not Available") + "\n"
            info_text += "Guild ID: " + web_info.get("guild_id", "Not Available") + "\n"
            themes.set_colored_result(result_thing, info_text, "Mauve")
    except Exception as e:
        themes.set_colored_result(result_thing, "thing went boom :(", "Red")
        console.print(e, style="red")
        return


def send_webhook_message():
    result_thing = "discord.discord_webhook_manager_result_text"
    url = dpg.get_value("discord.discord_webhook_manager_url_input").strip()
    if not url:
        themes.set_colored_result(result_thing, "you kinda forgot the url...", "Red")
        return

    message = dpg.get_value("discord.discord_webhook_manager_message_input").strip()
    if not message:
        themes.set_colored_result(result_thing, "you kinda forgot the message...", "Red")
        return
    themes.set_colored_result(result_thing, "sending message...", "Mauve")

    try:
        DiscordWebhook.send_message(url, message)

        themes.set_colored_result(result_thing, "sent message :3", "Mauve")
    except Exception as e:
        themes.set_colored_result(result_thing, "thing went boom :(", "Red")
        console.print(e, style="red")
        return

def edit_webhook():
    result_thing = "discord.discord_webhook_manager_result_text"
    url = dpg.get_value("discord.discord_webhook_manager_url_input").strip()
    if not url:
        themes.set_colored_result(result_thing, "you kinda forgot the url...", "Red")
        return

    name = dpg.get_value("discord.discord_webhook_manager_name_input").strip()
    avatar = dpg.get_value("discord.discord_webhook_manager_avatar_input").strip()
    channel_id = dpg.get_value("discord.discord_webhook_manager_channel_input").strip()
    if not name and not avatar and not channel_id:
        themes.set_colored_result(result_thing, "you kinda forgot the stuff...", "Red")
        return

    if channel_id:
        try:
            channel_id = int(channel_id)
        except Exception:
            themes.set_colored_result(result_thing, "id no real :(", "Red")
            return
    themes.set_colored_result(result_thing, "editing webhook...", "Mauve")

    try:
        DiscordWebhook.modify_webhook(url, name, avatar, channel_id)

        themes.set_colored_result(result_thing, "edited webhook :3", "Mauve")
    except Exception as e:
        themes.set_colored_result(result_thing, "thing went boom :(", "Red")
        console.print(e, style="red")
        return

def delete_webhook():
    result_thing = "discord.discord_webhook_manager_result_text"
    url = dpg.get_value("discord.discord_webhook_manager_url_input").strip()
    if not url:
        themes.set_colored_result(result_thing, "you kinda forgot the url...", "Red")
        return

    themes.set_colored_result(result_thing, "deleting webhook...", "Mauve")
    try:
        DiscordWebhook.delete_webhook(url)

        themes.set_colored_result(result_thing, "deleted webhook :3", "Mauve")
    except Exception as e:
        themes.set_colored_result(result_thing, "thing went boom :(", "Red")
        console.print(e, style="red")
        return