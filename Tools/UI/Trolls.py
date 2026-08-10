import dearpygui.dearpygui as dpg

import ColorPallets.Catpuccin.Mocha
import Tools.Backend.Trolls

import themes

def classdojo_account_locker():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="trolls.classdojo_account_locker",
            hint="Email",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Lock Account",
            callback=Tools.Backend.Trolls.classdojo_account_locker,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="trolls.classdojo_account_locker_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("trolls.classdojo_account_locker_result_text", themes.default_result_text, "Mauve")