import os
from win import gui

if not os.path.isdir("./data/"):
    os.mkdir("./data/")

if os.name == "nt":
    gui.main()
else:
    print(
        "Sorry, this platform isn't currently supported. Perhaps you could implement it and make a PR at https://github.com/obfuscatedgenerated/gmodCSSDownloader"
    )
