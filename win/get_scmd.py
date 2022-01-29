# Download:
# https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip

# Extract it to temp "data" folder

# GUI code will create a window with a frame, the frame will be passed to main, this code needs to pack a progressbar and other general info
def main(window, frame, successcallback, abortcallback):
    window.protocol("WM_DELETE_WINDOW", abortcallback)
    print("Fetching steamcmd...")
    print("Done.")
    successcallback()
