import dearpygui.dearpygui as dpg

import ColorPallets.Catpuccin.Mocha
import Tools.Backend.Internet

import themes

def find_name_servers():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="internet.find_name_servers_domain_input",
            hint="Domain",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Find Nameservers",
            callback=Tools.Backend.Internet.search_domain_nameservers,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="internet.find_name_servers_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("internet.find_name_servers_result_text", "thing happen here when you press the button :3", "Mauve")

def find_cert_domains():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="internet.find_cert_domains_ip_address_input",
            hint="IP Address/Domain",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Find Domains",
            callback=Tools.Backend.Internet.ip_cert_lookup,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="internet.find_cert_domains_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("internet.find_cert_domains_result_text", "thing happen here when you press the button :3", "Mauve")

def domain_to_ip():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="internet.domain_to_ip_domain_input",
            hint="Domain",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Dump DNS",
            callback=Tools.Backend.Internet.dns_dump,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="internet.domain_to_ip_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("internet.domain_to_ip_result_text", "thing happen here when you press the button :3", "Mauve")

def site_mapper():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="internet.site_mapper_domain_input",
            hint="Domain",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Map Site",
            callback=Tools.Backend.Internet.site_mapper,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="internet.site_mapper_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("internet.site_mapper_result_text", "thing happen here when you press the button :3", "Mauve")