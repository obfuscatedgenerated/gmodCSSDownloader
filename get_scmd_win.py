# Download:
#https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip

# Extract it to temp "data" folder

# GUI code will create a window with a frame, the frame will be passed to main, this code needs to pack a progressbar and other general info
def main(frame,callback):
    print("Fetching steamcmd...")
    print("Done.")
    callback()