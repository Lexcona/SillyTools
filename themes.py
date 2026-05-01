import dearpygui.dearpygui as dpg

import ColorPallets
from ColorPallets.Catpuccin import Mocha, Macchiato, Latte, Frappe

from Vars.General import console, default_result_text

current_theme = {}

def set_colored_result(tag: str, text: str, color_name: str = "Mauve"):
    try:
        if text != default_result_text:
            console.print(text, style=color_name.lower())
    except Exception:
        print(text)
    pallet = current_theme.get("pallet")
    if not pallet:
        dpg.set_value(tag, text)
        dpg.bind_item_theme(tag, text_like_theme)
        return

    color_map = {
        "Rosewater": pallet.Rosewater,
        "Flamingo":  pallet.Flamingo,
        "Pink":      pallet.Pink,
        "Mauve":     pallet.Mauve,
        "Red":       pallet.Red,
        "Maroon":    pallet.Maroon,
        "Peach":     pallet.Peach,
        "Yellow":    pallet.Yellow,
        "Green":     pallet.Green,
        "Teal":      pallet.Teal,
        "Sky":       pallet.Sky,
        "Sapphire":  pallet.Sapphire,
        "Blue":      pallet.Blue,
        "Lavender":  pallet.Lavender,
    }

    color = color_map.get(color_name, pallet.Mauve)

    with dpg.theme() as temp_text_color:
        with dpg.theme_component(dpg.mvInputText):
            dpg.add_theme_color(dpg.mvThemeCol_Text, color)

    dpg.set_value(tag, text)

    dpg.bind_item_theme(tag, text_like_theme)
    dpg.bind_item_theme(tag, temp_text_color)

with dpg.theme() as text_like_theme:
    with dpg.theme_component(dpg.mvInputText):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 0, 0, 0))
        dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 2)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 4)



with dpg.theme() as mocha_catppuccin_theme:
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

with dpg.theme() as macchiato_catppuccin_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Macchiato.Text)
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, Macchiato.Overlay0)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, Macchiato.Base)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, Macchiato.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, Macchiato.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_Border, Macchiato.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, Macchiato.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, Macchiato.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, Macchiato.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, Macchiato.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, Macchiato.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_Button, Macchiato.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, Macchiato.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, Macchiato.Overlay0)
        dpg.add_theme_color(dpg.mvThemeCol_Header, Macchiato.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, Macchiato.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, Macchiato.Overlay1)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, Macchiato.Blue)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, Macchiato.Sapphire)
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, Macchiato.Green)
        dpg.add_theme_color(dpg.mvThemeCol_Separator, Macchiato.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_Tab, Macchiato.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, Macchiato.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, Macchiato.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, Macchiato.Mantle)

        dpg.add_theme_color(dpg.mvThemeCol_PlotLines, Macchiato.Sky)
        dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, Macchiato.Peach)

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

with dpg.theme() as frappe_catppuccin_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Frappe.Text)
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, Frappe.Overlay0)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, Frappe.Base)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, Frappe.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, Frappe.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_Border, Frappe.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, Frappe.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, Frappe.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, Frappe.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, Frappe.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, Frappe.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_Button, Frappe.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, Frappe.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, Frappe.Overlay0)
        dpg.add_theme_color(dpg.mvThemeCol_Header, Frappe.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, Frappe.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, Frappe.Overlay1)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, Frappe.Blue)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, Frappe.Sapphire)
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, Frappe.Green)
        dpg.add_theme_color(dpg.mvThemeCol_Separator, Frappe.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_Tab, Frappe.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, Frappe.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, Frappe.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, Frappe.Mantle)

        dpg.add_theme_color(dpg.mvThemeCol_PlotLines, Frappe.Sky)
        dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, Frappe.Peach)

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

with dpg.theme() as latte_catppuccin_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Text, Latte.Text)
        dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, Latte.Overlay0)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, Latte.Base)
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, Latte.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_PopupBg, Latte.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_Border, Latte.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, Latte.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, Latte.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, Latte.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBg, Latte.Mantle)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, Latte.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_Button, Latte.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, Latte.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, Latte.Overlay0)
        dpg.add_theme_color(dpg.mvThemeCol_Header, Latte.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, Latte.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, Latte.Overlay1)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, Latte.Blue)
        dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, Latte.Sapphire)
        dpg.add_theme_color(dpg.mvThemeCol_CheckMark, Latte.Green)
        dpg.add_theme_color(dpg.mvThemeCol_Separator, Latte.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_Tab, Latte.Surface0)
        dpg.add_theme_color(dpg.mvThemeCol_TabHovered, Latte.Surface1)
        dpg.add_theme_color(dpg.mvThemeCol_TabActive, Latte.Surface2)
        dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, Latte.Mantle)

        dpg.add_theme_color(dpg.mvThemeCol_PlotLines, Latte.Sky)
        dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, Latte.Peach)

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

theme_dict = {
    "Catpuccin Mocca": {
        "theme": mocha_catppuccin_theme,
        "pallet": ColorPallets.Catpuccin.Mocha
    },
    "Catpuccin Macchiato": {
        "theme": macchiato_catppuccin_theme,
        "pallet": ColorPallets.Catpuccin.Macchiato
    },
    "Catpuccin Frappe": {
        "theme": frappe_catppuccin_theme,
        "pallet": ColorPallets.Catpuccin.Frappe
    },
    "Catpuccin Latte": {
        "theme": latte_catppuccin_theme,
        "pallet": ColorPallets.Catpuccin.Latte
    },
}