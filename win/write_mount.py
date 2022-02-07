import vdf
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os

if __name__ == "__main__":
    print("Importing as debug...")
    import icon
else:
    from win import icon


def abort(abortcbk, window):
    window.destroy()
    abortcbk()


def main(window, frame, gmodpath, assetspath, successcallback, abortcallback):
    window.protocol("WM_DELETE_WINDOW", lambda: abort(abortcallback, window))
    icon.seticon(window)
    window.resizable(False, False)
    print("Writing mount file...")
    proglabel = tk.Label(
        frame, text="Writing mount file...", background="black", foreground="white"
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
    if not os.path.exists(gmodpath + "\\cfg\\mount.cfg"):
        messagebox.showerror("Mount file not found", "Mount file not found. This might mean that you haven't launched Garry's Mod or that somehow the path changed (i.e. moved, renamed or deleted), or that something went wrong.")
        abortcallback()
        return
    with open(gmodpath + "\\cfg\\mount.cfg", "r+") as f: # TODO: check file exists and if not raise error prompt
        parsed = vdf.loads(f.read())
        if "cstrike" in parsed["mountcfg"]:
            if parsed["mountcfg"]["cstrike"] == os.path.abspath(assetspath):
                messagebox.showinfo("Already mounted", "The mount file already contains the path to the assets directory you specified.\nThis usually means that you've deleted, renamed or moved the assets from this installer before.\nIgnoring mount file write.")
                successcallback()
                return
            yn = messagebox.askyesno(
                "Mount File Conflict",
                "A value is already set for cstrike.\nDo you want to overwrite it?\nCurrent value: "+parsed["mountcfg"]["cstrike"],
            )
            if not yn:
                abort(abortcallback, window)
                return
        parsed["mountcfg"]["cstrike"] = os.path.abspath(assetspath)
        f.seek(0)
        f.truncate()
        f.write(vdf.dumps(parsed,pretty=True))
    successcallback()

if __name__ == "__main__":
    print("Running get mount GUI as debug...")
    dbg = tk.Tk()
    dbgf = tk.Frame(dbg, background="black")
    dbgf.pack()
    main(
        dbg,
        dbgf,
        "./testtemp",
        ".\\testtemp\\cstrike",
        lambda: print("Success!"),
        lambda: print("Abort!"),
    )