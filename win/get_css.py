import tkinter as tk
from tkinter import ttk
import asyncio
import os
import shutil

if __name__ == "__main__":
    print("Importing as debug...")
    import icon
else:
    from win import icon


def abort(abortcbk, window):
    try:
        # Stop the SteamCMD process in a few dire ways
        proc.kill()
        asyncio.get_event_loop().stop()
        os.popen("taskkill /im steamcmd.exe /f")  # last resort
    except RuntimeError as e:
        print("Thread was running but was told to stop. Oops!")
        print("Error was: " + str(e))
        pass
    window.destroy()
    # Defer to the abort callback
    abortcbk()


curr_window = None
poutputtext = None
proc = None


def puts(text):
    print(text)
    poutputtext.insert(tk.END, "\n")
    poutputtext.insert(tk.END, text)
    poutputtext.see(tk.END)


async def updatewin():
    # Keeps the window responsive whilst the asyncio task runs
    while True:
        curr_window.update()
        await asyncio.sleep(0.05)


async def update_poutput_loop(pipe, type):
    tout = 0
    while True:
        if type == "err":
            # Read from stderr @ 1024 bytes
            raise Exception(await pipe.read(1024))
        else:
            # Read from stdout @ 1024 bytes
            pr = await pipe.read(1024)
            # Check if we have any data
            if pr == b"":
                tout += 1
                if tout > 5:
                    print("Got blank output from SteamCMD 5 times, breaking loop...")
                    break
            puts(pr)


async def fetch_css(steamcmd_path, username, password):
    global proc
    print("Using SteamCMD to fetch CS:S...")
    # Create a shell to make SteamCMD download CS:S server files
    loop = asyncio.get_event_loop()
    proc = await asyncio.create_subprocess_shell(
        steamcmd_path
        + " +force_install_dir "
        + os.path.abspath("./data/")
        + " +login "
        + username
        + " "
        + password
        + " +app_update 232330 -validate +quit",
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    # Feed the output to the update loop
    loop.create_task(update_poutput_loop(proc.stdout, "out"))
    loop.create_task(update_poutput_loop(proc.stderr, "err"))
    loop.create_task(updatewin())
    await proc.wait()


def main(
    window,
    frame,
    steamcmd_path,
    assetspath,
    username,
    password,
    successcallback,
    abortcallback,
):
    global curr_window, poutputtext
    curr_window = window
    # Call abort on window close
    curr_window.protocol("WM_DELETE_WINDOW", lambda: abort(abortcallback, window))
    icon.seticon(window)
    window.resizable(False, False)
    print("Fetching CSS...")
    print("With SteamCMD: " + steamcmd_path)
    # Create the UI
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
    # Stop the text from being editable without any weird state tricks
    poutputtext.bind("<Key>", lambda e: "break")
    poutputtext.bind("<Button-1>", lambda e: "break")
    curr_window.update()
    # Start the asyncio task loops
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(
        fetch_css(steamcmd_path, username, password)
    )
    # Reset the UI
    for widget in frame.winfo_children():
        widget.destroy()
    proglabel = tk.Label(
        frame, text="Moving files...", background="black", foreground="white"
    )
    proglabel.pack()
    progress = ttk.Progressbar(
        frame, orient="horizontal", length=300, mode="indeterminate"
    )
    progress["value"] = 0
    progress["maximum"] = 100
    progress.pack()
    progress.start()
    window.update()
    print("Moving files...")
    # Move the files to the assets folder
    shutil.move("./data/cstrike/", assetspath, copy_function=shutil.copytree)
    # TODO: delete non-assets (might not be important and it lets steamcmd know that the install finished fully, maybe leave it)
    print("Done!")
    # Call the success callback
    successcallback()


if __name__ == "__main__":
    print("Running get CSS GUI as debug...")
    dbg = tk.Tk()
    dbgf = tk.Frame(dbg, background="black")
    dbgf.pack()
    main(
        dbg,
        dbgf,
        "steamcmd",
        "./data/",
        "anonymous",
        "",
        lambda: print("Success!"),
        lambda: print("Abort!"),
    )
