import os
import shutil
from pathlib import Path

OUT_DIR = Path("desilly")
SCAN_DIR = Path(".")

# Clean previous output
if OUT_DIR.exists():
    shutil.rmtree(OUT_DIR)
    print("Cleaned old desilly folder")

print("Starting desilly process...")

for root, dirs, files in os.walk(SCAN_DIR, topdown=True):
    # === BETTER SKIPPING ===
    # Skip entire directories we don't want
    dirs[:] = [d for d in dirs if d not in (".venv", "__pycache__", ".git", ".idea")]

    # Also skip if we're already inside one of those folders
    if any(skip in Path(root).parts for skip in [".venv", "__pycache__", ".git", ".idea"]):
        continue

    # Get clean relative path (this fixes the nesting bug)
    try:
        rel_path = Path(root).relative_to(SCAN_DIR)
    except ValueError:
        rel_path = Path("")

    output_dir = OUT_DIR / rel_path
    output_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        # Skip the script itself and .gitignore
        if file in ("desilly.py", ".gitignore"):
            continue

        src_file = Path(root) / file
        dst_file = output_dir / file

        try:
            data = src_file.read_bytes()

            # Try to treat as text and remove :3 / :(
            try:
                text = data.decode("utf-8")
                original_len = len(text)

                text = (text
                        .replace(" :3", "")
                        .replace(":3", "")
                        .replace(" :(", "")
                        .replace(":(", "")
                        )

                if len(text) != original_len:
                    print(f"Cleaned :3/:( from {src_file}")

                data = text.encode("utf-8")
            except UnicodeDecodeError:
                pass  # Binary file (images, etc.) - copy as-is

            dst_file.write_bytes(data)

        except Exception as e:
            print(f"Error processing {src_file}: {e}")

print("Done! Check the 'desilly' folder.")