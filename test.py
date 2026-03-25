def replace_placeholders(text: str, name: str, value: str):
    vars = []
    text_split = text.split("[")
    print(text_split)
    i = 0
    for textt in text_split:
        if textt.endswith("]"):
            vars.append(textt.split("]")[0])
        i += 1

replace_placeholders("https://github.com/[username][cool]", "username", "cool")