import tkinter as tk
from tkinter import ttk
import asyncio
import os


def abort(abortcbk, window):
    try:
        proc.kill()
        asyncio.get_event_loop().stop()
        os.system("taskkill /im steamcmd.exe /f") # last resort
    except RuntimeError as e:
        print("Thread was running but was told to stop. Oops!")
        print("Error was: " + str(e))
        pass
    window.destroy()
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
    while True:
        curr_window.update()
        await asyncio.sleep(0.05)


async def update_poutput_loop(pipe, type):
    while True:
        if type == "err":
            raise Exception(await pipe.read(1024))
        else:
            puts(await pipe.read(1024))


async def fetch_css(steamcmd_path, username, password):
    global proc
    print("Using SteamCMD to fetch CS:S...")
    loop = asyncio.get_event_loop()
    proc = await asyncio.create_subprocess_shell(
        steamcmd_path
        + " +force_install_dir "+os.path.abspath("./data/")+" +login "
        + username
        + " "
        + password
        + " +app_update 232330 -validate +quit",
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
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
    curr_window.protocol("WM_DELETE_WINDOW", lambda: abort(abortcallback, window))
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
    curr_window.update()
    asyncio.set_event_loop(asyncio.new_event_loop())
    asyncio.get_event_loop().run_until_complete(
        fetch_css(steamcmd_path, username, password)
    )
    # move assets to selected folder
    # delete non-assets
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
        "steamcmd",
        "./data/",
        "anonymous",
        "",
        lambda: print("Success!"),
        lambda: print("Abort!"),
    )
