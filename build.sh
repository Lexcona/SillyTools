#!/bin/bash
set -e
rm -rf builds
mkdir -p builds/Linux builds/Windows

PROJECT_ROOT=$(pwd)

echo "=== Building Linux version ==="
cd builds/Linux || exit 1

echo "Installing dependencies..."

python3 -m pip install -r "${PROJECT_ROOT}/requirements.txt"

python3 -m PyInstaller \
  --onedir \
  --clean \
  --name "SillyTools" \
  --add-data "${PROJECT_ROOT}/Assets:Assets" \
  --add-data "${PROJECT_ROOT}/Fonts:Fonts" \
  --windowed \
  --icon "${PROJECT_ROOT}/Assets/icon.png" \
  "${PROJECT_ROOT}/main.py"

echo "=== Building Windows version with Wine ==="
cd ../Windows || exit 1

WINE_PYTHON="C:\\Python314\\python.exe"

echo "Installing dependencies inside Wine..."
wine "$WINE_PYTHON" -m pip install -r "${PROJECT_ROOT}/requirements.txt" || echo "Warning: pip install may have issues (some packages don't install cleanly under Wine)"

echo "Running PyInstaller for Windows..."
wine "$WINE_PYTHON" -m PyInstaller \
  --onedir \
  --clean \
  --name "SillyTools" \
  --add-data "${PROJECT_ROOT}/Assets;Assets" \
  --add-data "${PROJECT_ROOT}/Fonts;Fonts" \
  --windowed \
  --icon "${PROJECT_ROOT}/Assets/icon.png" \
  "${PROJECT_ROOT}/main.py"

echo "=== Builds finished! ==="
echo "Linux  build → $(pwd)/../Linux/dist/SillyTools/"
echo "Windows build → $(pwd)/dist/SillyTools/"
