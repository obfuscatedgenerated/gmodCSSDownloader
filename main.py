import os
from __version__ import __version__
from win import gui

print("Version: " + __version__)

# Make data dir if it doesn't exist
if not os.path.isdir("./data/"):
    os.mkdir("./data/")

if os.name == "nt":
    # Defer to the GUI script
    gui.main()
else:
    print(
        "Sorry, this platform isn't currently supported. Perhaps you could implement it and make a PR at https://github.com/obfuscatedgenerated/gmodCSSDownloader"
    )
