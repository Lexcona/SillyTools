import os

import requests

from bs4 import BeautifulSoup
from rich.console import Console

console = Console()

console.print("Sending request to catppuccin.", style="cyan")
res = requests.get("https://catppuccin.com/palette/")
res.raise_for_status()
console.print("Request successfully sent.", style="green")

soup = BeautifulSoup(res.content, "html.parser")

output_dir = "../ColorPallets/Catpuccin"

pallets = []

console.print("Finding all color pallets.")
for pallet in soup.find_all("div", class_="flavor"):
    pallet_data = {
        "name": "",
        "colors": []
    }
    for span in pallet.find_all("span"):
        data_flavor = span.get("data-flavor")
        if data_flavor:
            pallet_data["name"] = data_flavor
            console.print(f"Found color pallet: {data_flavor}", style="cyan")
            break
    
    for color in pallet.find_all("tr"):
        color_data = {
            "name": "",
            "rgb": ""
        }
        raw_color_name = color.find("h5", class_="color-name")
        if raw_color_name != None:
            color_data["name"] = raw_color_name.text
            console.print(f"Found color: {color_data['name']}", style="cyan")
            raw_color_rgb_tag = color.find("td", class_="color-rgb")
            color_data["rgb"] = raw_color_rgb_tag.find("astro-slot").text.split("(")[-1].split(")")[0]

            pallet_data["colors"].append(color_data)

    pallets.append(pallet_data)

    console.print(f"Added color pallet: {pallet_data}", style="green")

for pallet in pallets:
    console.print(f"Generating Python file for {pallet['name']}", style="cyan")
    color_lines = []
    for color in pallet["colors"]:
        color_line = f"{color['name'].strip().replace(" ", "")} = [{color['rgb'].strip()}, 255]"
        color_lines.append(color_line)
    output = f"../ColorPallets/Catpuccin/{pallet['name'].capitalize().strip()}.py"
    os.makedirs(output_dir, exist_ok=True)
    with open(output, "w+") as f:
        f.write("\n".join(color_lines))
    with open("../ColorPallets/__init__.py", "w+") as f:
        f.write("from ColorPallets.Catpuccin import *")
    console.print(f"Outputed {pallet['name']} to {output}", style="green")

console.print("Finished generating files.", style="cyan")