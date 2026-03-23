import dearpygui.dearpygui as dpg

import ColorPallets.Catpuccin.Mocha
import Tools.Backend.Discord

import themes

def discord_webhook_manager():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="discord.discord_webhook_manager_url_input",
            hint="URL",
            width=450
        )

    dpg.add_spacer(height=12)

    dpg.add_button(
        label="Get Webhook Info",
        callback=Tools.Backend.Discord.get_webhook_info,
        user_data=None,
        width=450
    )

    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="discord.discord_webhook_manager_message_input",
            hint="Message",
            width=325
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Send Message",
            callback=Tools.Backend.Discord.send_webhook_message,
            user_data=None
        )

    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="discord.discord_webhook_manager_name_input",
            hint="Name",
            width=103
        )

        dpg.add_input_text(
            tag="discord.discord_webhook_manager_avatar_input",
            hint="URL",
            width=103
        )

        dpg.add_input_text(
            tag="discord.discord_webhook_manager_channel_input",
            hint="Channel ID",
            width=103
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Edit Webhook",
            callback=Tools.Backend.Discord.edit_webhook,
            user_data=None
        )

    dpg.add_button(
        label="Delete Webhook",
        callback=Tools.Backend.Discord.get_webhook_info,
        user_data=None,
        width=450
    )

    dpg.add_input_text(
        default_value="",
        tag="discord.discord_webhook_manager_result_text",
        multiline=True,
        width=450,
        height=185,
        readonly=True
    )

    themes.set_colored_result("discord.discord_webhook_manager_result_text",themes.default_result_text, "Mauve")