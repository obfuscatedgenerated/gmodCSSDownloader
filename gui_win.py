import tkinter as tk
from tkinter import messagebox
import asyncio


def close_windows():
    raise SystemExit


async def check_scmd():
    proc = await asyncio.create_subprocess_shell(
        "where steamcmd", stderr=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()
    if stderr:
        if stderr.startswith(b"INFO:"):
            return False
        else:
            raise Exception(stderr.decode())
    else:
        return stdout.decode().strip()


def find_gmod():
    # HKEY_CURRENT_USER\SOFTWARE\Valve\Steam
    # SteamPath
    # Use this to find libraryfolders.vdf, then parse it as json, find gmod install path (gmod app id = 4000), then autofill the path into the textbox
    # If failed, see if gmod exists on the default install path
    # If failed, ask the user to manually enter the path
    return None


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master, background="black")
        self.master.title("gmodCSSDownloader - Main GUI")
        # self.master.iconbitmap("icon.ico")
        self.frame.pack()
        self.master.protocol("WM_DELETE_WINDOW", close_windows)
        if asyncio.run(check_scmd()) == False:
            yn = messagebox.askyesno(
                "Not found",
                "SteamCMD not found in the PATH. Do you want to download it to the data directory?",
            )
            if yn:
                self.master.withdraw()
                self.create_scmd_progress(
                    self.scmd_success_callback, self.scmd_abort_callback
                )

    def create_scmd_progress(self, successcallback, abortcallback):
        self.scmd_window = tk.Toplevel(self.master)
        self.app = SCMD_Progress(self.scmd_window, successcallback, abortcallback)

    def scmd_success_callback(self):
        self.scmd_window.destroy()
        self.master.deiconify()

    def scmd_abort_callback(self):
        self.master.deiconify()
        messagebox.showerror("Aborted", "SteamCMD download was aborted!")


class SCMD_Progress:
    def __init__(self, master, successcallback, abortcallback):
        self.master = master
        self.frame = tk.Frame(self.master, background="black")
        self.master.title("gmodCSSDownloader - SteamCMD Progress")
        import get_scmd_win

        get_scmd_win.main(self.master, self.frame, successcallback, abortcallback)


def main():
    print("Launching GUI...")
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    print("Launching GUI as debug...")
    main()


# File select: Where to save?
# File select or perhaps auto detect: gmod path
# Optional input: use credentials? (default: anonymous)
