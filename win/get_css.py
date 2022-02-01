# Use popen pipe to show status in gui textbox

# Save to the temp "data" folder

# Move assets to selected folder

# Delete non-assets


def abort(abortcbk,window):
    window.destroy()
    abortcbk()


def main(window, frame, steamcmd_path, gmodpath, assetspath, username, password, successcallback, abortcallback):
    window.protocol("WM_DELETE_WINDOW", lambda: abort(abortcallback,window))
    print("Fetching CSS...")
    print("With SteamCMD: "+steamcmd_path)
    print("Done!")
    successcallback()
