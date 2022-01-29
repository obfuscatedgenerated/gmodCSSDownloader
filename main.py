import os

if not os.path.isdir("./data/"):
    os.mkdir("./data/")

if os.name == "nt":
    import gui_win
else:
    print("Sorry, this platform isn't currently supported. Perhaps you could implement it and make a PR at https://github.com/obfuscatedgenerated/gmodCSSDownloader")
