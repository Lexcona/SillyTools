import dearpygui.dearpygui as dpg

from ColorPallets.Catpuccin import Mocha

default_result_text = "thing happen here when you press the button :3"

def set_colored_result(tag: str, text: str, color_name: str = "Mauve"):
    color_themes = {
        "Rosewater": result_rosewater,
        "Flamingo": result_flamingo,
        "Pink": result_pink,
        "Mauve": result_mauve,
        "Red": result_red,
        "Maroon": result_maroon,
        "Peach": result_peach,
        "Yellow": result_yellow,
        "Green": result_green,
        "Teal": result_teal,
        "Sky": result_sky,
        "Sapphire": result_sapphire,
        "Blue": result_blue,
        "Lavender": result_lavender,
    }

    dpg.set_value(tag, text)
    theme = color_themes.get(color_name, result_mauve)
    dpg.bind_item_theme(tag, text_like_theme)
    dpg.bind_item_theme(tag, theme)

with dpg.theme() as text_like_theme:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 2)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 4)

with dpg.theme() as result_rosewater:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Rosewater)

with dpg.theme() as result_flamingo:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Flamingo)

with dpg.theme() as result_pink:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Pink)

with dpg.theme() as result_mauve:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Mauve)

with dpg.theme() as result_red:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Red)

with dpg.theme() as result_maroon:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Maroon)

with dpg.theme() as result_peach:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Peach)

with dpg.theme() as result_yellow:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Yellow)

with dpg.theme() as result_green:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Green)

with dpg.theme() as result_teal:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Teal)

with dpg.theme() as result_sky:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Sky)

with dpg.theme() as result_sapphire:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Sapphire)

with dpg.theme() as result_blue:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Blue)
        
with dpg.theme() as result_lavender:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Lavender)

with dpg.theme() as catppuccin_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Mocha.Text)
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, Mocha.Overlay0)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, Mocha.Base)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, Mocha.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, Mocha.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_Border, Mocha.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, Mocha.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, Mocha.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, Mocha.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, Mocha.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, Mocha.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_Button, Mocha.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, Mocha.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, Mocha.Overlay0)
        dpg.add_theme_color(dpg.mvThemeCol_Header, Mocha.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, Mocha.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, Mocha.Overlay1)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, Mocha.Blue)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, Mocha.Sapphire)
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, Mocha.Green)
        dpg.add_theme_color(dpg.mvThemeCol_Separator, Mocha.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_Tab, Mocha.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, Mocha.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, Mocha.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, Mocha.Mantle)

        dpg.add_theme_color(dpg.mvThemeCol_PlotLines, Mocha.Sky)
        dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, Mocha.Peach)

        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
        dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 12)
        dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
        dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 6)

        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 6)
        dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 4, 4)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 4)
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 10)