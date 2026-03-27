import os
import shutil

out_dir = "desilly"
scan_dir = "./"

if os.path.exists(out_dir):
    shutil.rmtree(out_dir)

for path, directories, files in os.walk(scan_dir):
    thingy = os.path.join(out_dir, path)
    os.makedirs(thingy, exist_ok=True)
    if not ".venv" in path and not "__pycache__" in path and not ".git" in path and not ".idea" in path:
        for file in files:
            if not file in ("desilly.py", ".gitignore"):
                cool = os.path.join(thingy, file)

                with open(cool, "r") as f:
                    data = f.read()

                data = data.replace(" :3", "").replace(":3", "").replace(" :(", "").replace(":(", "")

                with open(cool, "w+") as f:
                    f.write(data)
