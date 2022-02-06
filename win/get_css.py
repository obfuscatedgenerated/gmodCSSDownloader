# Use popen pipe to show status in gui textbox

# Save to the temp "data" folder

# Move assets to selected folder

# Delete non-assets

import tkinter as tk
from tkinter import ttk


def abort(abortcbk, window):
    window.destroy()
    abortcbk()


poutputtext = None


def puts(text):
    poutputtext.insert(tk.END, text)
    poutputtext.see(tk.END)


def main(
    window,
    frame,
    steamcmd_path,
    gmodpath,
    assetspath,
    username,
    password,
    successcallback,
    abortcallback,
):
    global poutputtext
    window.protocol("WM_DELETE_WINDOW", lambda: abort(abortcallback, window))
    print("Fetching CSS...")
    print("With SteamCMD: " + steamcmd_path)
    proglabel = tk.Label(
        frame, text="Fetching CS:S Assets...", background="black", foreground="white"
    )
    proglabel.pack()
    progress = ttk.Progressbar(
        frame, orient="horizontal", length=300, mode="indeterminate"
    )
    progress["value"] = 0
    progress["maximum"] = 100
    progress.pack()
    progress.start()
    poutputtext = tk.Text(
        frame, height=15, width=50, background="black", foreground="white"
    )
    poutputtext.pack()
    window.update()
    print("Done!")
    successcallback()


if __name__ == "__main__":
    print("Runnning get CSS GUI as debug...")
    dbg = tk.Tk()
    dbgf = tk.Frame(dbg, background="black")
    dbgf.pack()
    main(
        dbg,
        dbgf,
        "./steamcmd.exe",
        "./gmod",
        "./assets",
        "username",
        "password",
        lambda: print("Success!"),
        lambda: print("Abort!"),
    )
    puts("Test!\n")
    dbg.mainloop()
