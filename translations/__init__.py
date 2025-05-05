import json

data = "langs loaded"

translations = {}

# with open("./translations/localename.json", "r", encoding="utf-8") as lang:
#     json_data = json.load(lang)
#     translations["lang"] = json_data

with open("./translations/En-us.json", "r", encoding="utf-8") as en:
    json_data = json.load(en)
    translations["en"] = json_data