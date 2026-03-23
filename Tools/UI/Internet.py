import dearpygui.dearpygui as dpg

import ColorPallets.Catpuccin.Mocha
import Libs.General
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

    themes.set_colored_result("internet.find_name_servers_result_text", themes.default_result_text, "Mauve")

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

    themes.set_colored_result("internet.find_cert_domains_result_text", themes.default_result_text, "Mauve")

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

    themes.set_colored_result("internet.domain_to_ip_result_text", themes.default_result_text, "Mauve")

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

    themes.set_colored_result("internet.site_mapper_result_text", themes.default_result_text, "Mauve")

def tag_dumper():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="internet.tag_dumper_url_input",
            hint="URL",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Dump Tags",
            callback=Tools.Backend.Internet.tag_dumper,
            user_data=None
        )

    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="internet.tag_dumper_output_input",
            hint="Directory",
            width=300
        )

        #dpg.add_spacer(width=8)
        dpg.add_button(label="Select Folder", callback=lambda: dpg.show_item("internet.tag_dumper_dir_dialog"))

        dpg.file_dialog(
            directory_selector=True,
            show=False,
            callback=Libs.General.dir_callback,
            tag="internet.tag_dumper_dir_dialog",
            user_data="internet.tag_dumper_output_input"
        )


    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="internet.tag_dumper_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("internet.tag_dumper_result_text", themes.default_result_text, "Mauve")

def method_scanner():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="internet.method_scanner_url_input",
            hint="URL",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Find Methods",
            callback=Tools.Backend.Internet.method_scanner,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="internet.method_scanner_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("internet.method_scanner_result_text", themes.default_result_text, "Mauve")

def url_checker():
    dpg.add_input_text(
        tag="internet.url_checker_urls_input",
        hint="URLs",
        multiline=True,
        width=480,
        height=185,
    )

        #dpg.add_spacer(width=8)

    dpg.add_button(
        label="Check URLS",
        callback=Tools.Backend.Internet.url_checker,
        user_data=None,
        width=480,
    )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="internet.url_checker_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("internet.url_checker_result_text", themes.default_result_text, "Mauve")

def website_info():
    with dpg.group(horizontal=True):
        dpg.add_input_text(
            tag="internet.website_info_url_input",
            hint="URL",
            width=300
        )

        #dpg.add_spacer(width=8)

        dpg.add_button(
            label="Find Info",
            callback=Tools.Backend.Internet.website_info,
            user_data=None
        )

    dpg.add_spacer(height=12)

    dpg.add_input_text(
        default_value="",
        tag="internet.website_info_result_text",
        multiline=True,
        width=480,
        height=185,
        readonly=True
    )

    themes.set_colored_result("internet.website_info_result_text", themes.default_result_text, "Mauve")
