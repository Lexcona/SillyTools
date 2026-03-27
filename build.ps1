rm -rf build dist *.spec

pyinstaller --onedir --clean --name "SillyTools" --add-data "Assets:Assets" --add-data "Fonts:Fonts" --windowed --icon=Assets/icon.png main.py