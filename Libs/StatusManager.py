class StatusManager:
    def __init__(self, path="settings.json"):
        self.data = {}

    def write(self, path: str, value):
        parts = path.split("/")
        data = self.data
        for part in parts[:-1]:
            if part not in data or not isinstance(data[part], dict):
                data[part] = {}
            data = data[part]
        data[parts[-1]] = value

    def read(self, path: str, default=None):
        data = self.data
        for part in path.split("/"):
            if isinstance(data, dict) and part in data:
                data = data[part]
            else:
                return default
        if isinstance(data, str):
            if data.replace(" ", "") == "":
                return default

        return data

    def reset(self, path:str):
        if isinstance(self.read(path), list):
            self.write(path, [])
        else:
            self.write(path, {})


status = StatusManager()