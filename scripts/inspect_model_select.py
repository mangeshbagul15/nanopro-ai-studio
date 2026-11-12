with open("app/ui/global_ai_lab_view.py", "r", encoding="utf-8") as f:
    text = f.read()

idx = text.find("ailabModelSelect")
print(text[idx:idx+1500].encode("ascii", "backslashreplace").decode("ascii"))
