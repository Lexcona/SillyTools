import json
from Libs.Wrappers import Mojang

print(json.dumps(Mojang.get_skin_data("LocalSody"), indent=4))