import os
import json

class ConfigManager:
    def __init__(self, path="settings.json"):
        self.path = path
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def write(self, path: str, value):
        parts = path.split("/")
        data = self.data
        for part in parts[:-1]:
            if part not in data or not isinstance(data[part], dict):
                data[part] = {}
            data = data[part]
        data[parts[-1]] = value
        self.save()

    def read(self, path: str, default=None):
        data = self.data
        for part in path.split("/"):
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                return default
        return data

config = ConfigManager()