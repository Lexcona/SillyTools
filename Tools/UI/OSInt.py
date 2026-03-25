import dearpygui.dearpygui as dpg

import ColorPallets.Catpuccin.Mocha
import Tools.Backend.OSInt

import themes

def github_email_search():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="osint.github_email_search_input",
            hint="Username/URL",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Find Emails",
            callback=Tools.Backend.OSInt.search_emails_callback,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="osint.github_email_search_input_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("osint.github_email_search_input_result_text", themes.default_result_text, "Mauve")

def ip_lookup():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="osint.ip_lookup_ip_input",
            hint="IP Address",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Lookup IP",
            callback=Tools.Backend.OSInt.ip_lookup,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="osint.ip_lookup_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )
    themes.set_colored_result("osint.ip_lookup_result_text", themes.default_result_text, "Mauve")

def username_search():

    dpg.add_input_text(
        tag="osint.username_search_username_input",
        hint="Username",
        width=480,
        height=185,
        multiline=True
    )

    dpg.add_button(
        label="Lookup Username",
        callback=Tools.Backend.OSInt.username_search,
        user_data=None,
        width=480
    )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="osint.username_search_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )
    themes.set_colored_result("osint.username_search_result_text", themes.default_result_text, "Mauve")
