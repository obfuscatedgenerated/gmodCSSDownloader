import requests
import tkinter as tk
from tkinter import ttk
from zipfile import ZipFile
import shutil
import os

res = None

def abort(abortcbk,window):
    if res is not None:
        res.close()
    window.destroy()
    abortcbk()


# GUI code will create a window with a frame, the frame will be passed to main, this code needs to pack a progressbar and other general info
def main(window, frame, successcallback, abortcallback):
    window.protocol("WM_DELETE_WINDOW", lambda: abort(abortcallback,window))
    print("Fetching steamcmd...")
    progvar = tk.StringVar(frame, value="Downloading SteamCMD... (0/0 0%)")
    proglabel = tk.Label(frame, textvariable=progvar, background="black", foreground="white")
    proglabel.pack()
    progress = ttk.Progressbar(frame, orient="horizontal",length=300, mode="determinate")
    progress["value"] = 0
    progress["maximum"] = 100    
    progress.pack()
    window.update()
    dlpath = "./data/steamcmd.zip"
    with open(dlpath,"wb") as f:
        res = requests.get("https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip", stream=True)
        length = res.headers.get("Content-Length")
        if length is None:
            print("Got no Content-Length header, writing direct to file...")
            f.write(res.content)
        else:
            downloaded = 0
            length = int(length)
            for data in res.iter_content(chunk_size=4096):
                downloaded += len(data)
                f.write(data)
                percent_dl = int(100 * (downloaded / length))
                print("DL Percent: " + str(percent_dl)+"%")
                progress["value"] = percent_dl
                progvar.set("Downloading SteamCMD... ("+str(downloaded)+"/"+str(length)+" "+str(percent_dl)+"%)")
                window.update_idletasks()
    print("Done.")
    print("Extracting...")
    for widget in frame.winfo_children():
        widget.destroy()
    progvar = tk.StringVar(frame, value="Extracting...")
    proglabel = tk.Label(frame, textvariable=progvar, background="black", foreground="white")
    proglabel.pack()
    progress = ttk.Progressbar(frame, orient="horizontal",length=300, mode="indeterminate")
    progress["value"] = 0
    progress["maximum"] = 100    
    progress.pack()
    progress.start()
    window.update()
    with ZipFile("./data/steamcmd.zip", 'r') as zipf:
        with zipf.open("steamcmd.exe") as srcf, open("./data/steamcmd.exe","wb") as targf:
            shutil.copyfileobj(srcf, targf)
    os.remove("./data/steamcmd.zip")
    successcallback()