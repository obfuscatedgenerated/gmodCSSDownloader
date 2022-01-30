import tkinter as tk
from tkinter import messagebox
import asyncio
import winreg
import os
import vdf

regtypeReverseLookup = ["REG_NONE","REG_SZ","REG_EXPAND_SZ","REG_BINARY","REG_DWORD_LITTLE_ENDIAN","REG_DWORD_BIGENDIAN","REG_LINK","REG_MULTI_SZ","REG_RESOURCE_LIST","REG_FULL_RESOURCE_DESCRIPTOR","REG_RESOURCE_REQUIREMENTS_LIST","REG_QWORD_LITTLE_ENDIAN"] # REG_DWORD defaults to REG_DWORD_LITTLE_ENDIAN, REG_QWORD defaults to REG_QWORD_LITTLE_ENDIAN

if __name__ == "__main__":
    print("Importing as debug...")
    import get_scmd
    import get_css
    import write_mount
else:
    from win import get_scmd
    from win import get_css
    from win import write_mount


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
    try:
        print("Finding Steam...")
        reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        reg_key = winreg.OpenKey(reg_connection, r"SOFTWARE\\Valve\\Steam")
        reg_value = winreg.QueryValueEx(reg_key, "SteamPath")
        if reg_value[1] != winreg.REG_SZ:
            print("Invalid type for SteamPath. Expected REG_SZ (int: 1), got "+regtypeReverseLookup[reg_value[1]]+" (int: "+str(reg_value[1])+")")
            raise OSError("Invalid type for SteamPath. Expected REG_SZ (int: 1), got "+regtypeReverseLookup[reg_value[1]]+" (int: "+str(reg_value[1])+")")
        print(reg_value[0])
        if os.path.isfile(reg_value[0]+"/steamapps/libraryfolders.vdf"):
            print("Using libraryfolders.vdf...")
            try:
                parsed = vdf.parse(open(reg_value[0]+"/steamapps/libraryfolders.vdf", "r"))
                libfolders = parsed["libraryfolders"]
                del libfolders["contentstatsid"]
                for lf in libfolders:
                    print("Searching in "+libfolders[lf]["path"]+"...")
                    if "4000" in libfolders[lf]["apps"]:
                        print("Found gmod app ID! Checking path...")
                        if os.path.isdir(libfolders[lf]["path"]+"\\steamapps\\common\\GarrysMod\\garrysmod"):
                            print("Found Garry's Mod!")
                            print(libfolders[lf]["path"]+"\\steamapps\\common\\GarrysMod\\garrysmod")
                            return libfolders[lf]["path"]+"\\steamapps\\common\\GarrysMod\\garrysmod"
                        else:
                            print("Couldn't find Garry's Mod in this library folder despite it being listed in libraryfolders.vdf! Skipping...")
                raise FileNotFoundError("Could not find gmod in libraryfolders.vdf")
            except (SyntaxError, AttributeError) as e:
                print("Could not parse libraryfolders.vdf\n"+str(e))
                print("Failed to parse libraryfolders.vdf. Trying steamapps/common default path...")
                # then autofill the path into the textbox
        else:
            print("Failed to find libraryfolders.vdf. Trying steamapps/common default path...")
    except (OSError, WindowsError, EnvironmentError, FileNotFoundError) as e:
        print("Failed to find Steam.\n"+str(e))
        print("Steam not found, trying default programfiles(x86) path...")
        print("Not found in programfiles(x86), user must enter path manually.")
        # If failed, see if gmod exists on the path where Steam was
        # If failed, see if gmod exists on the default install path
        # If failed, ask the user to manually enter the path
    return ""


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
        find_gmod()

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
