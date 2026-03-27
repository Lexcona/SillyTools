import dearpygui.dearpygui as dpg
import Tools.Backend.GeneralInfo
import themes

def minecraft_lookup():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="generalInfo.minecraft_lookup_username_input",
            hint="Username",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Lookup Username",
            callback=Tools.Backend.GeneralInfo.minecraft_lookup,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="generalInfo.minecraft_lookup_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )
    themes.set_colored_result("generalInfo.minecraft_lookup_result_text", themes.default_result_text, "Mauve")