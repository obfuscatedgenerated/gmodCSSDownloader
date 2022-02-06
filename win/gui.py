import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import asyncio
import winreg
import os
import vdf

regtypeReverseLookup = [
    "REG_NONE",
    "REG_SZ",
    "REG_EXPAND_SZ",
    "REG_BINARY",
    "REG_DWORD_LITTLE_ENDIAN",
    "REG_DWORD_BIGENDIAN",
    "REG_LINK",
    "REG_MULTI_SZ",
    "REG_RESOURCE_LIST",
    "REG_FULL_RESOURCE_DESCRIPTOR",
    "REG_RESOURCE_REQUIREMENTS_LIST",
    "REG_QWORD_LITTLE_ENDIAN",
]  # REG_DWORD defaults to REG_DWORD_LITTLE_ENDIAN, REG_QWORD defaults to REG_QWORD_LITTLE_ENDIAN

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
            if not os.path.isfile("./data/steamcmd.exe"):
                return False
            else:
                return "./data/steamcmd.exe"
        else:
            raise Exception(stderr.decode())
    else:
        return stdout.decode().strip()


def find_gmod():
    try:
        # Use the registry to locate Steam's install path
        print("Finding Steam...")
        reg_connection = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        reg_key = winreg.OpenKey(reg_connection, r"SOFTWARE\\Valve\\Steam")
        reg_value = winreg.QueryValueEx(reg_key, "SteamPath")
        if reg_value[1] != winreg.REG_SZ:
            print(
                "Invalid type for SteamPath. Expected REG_SZ (int: 1), got "
                + regtypeReverseLookup[reg_value[1]]
                + " (int: "
                + str(reg_value[1])
                + ")"
            )
            raise OSError(
                "Invalid type for SteamPath. Expected REG_SZ (int: 1), got "
                + regtypeReverseLookup[reg_value[1]]
                + " (int: "
                + str(reg_value[1])
                + ")"
            )
        print(reg_value[0])
        if os.path.isfile(reg_value[0] + "/steamapps/libraryfolders.vdf"):
            print("Using libraryfolders.vdf...")
            try:
                # Parse the libraryfolders.vdf file
                parsed = vdf.parse(
                    open(reg_value[0] + "/steamapps/libraryfolders.vdf", "r")
                )
                libfolders = parsed["libraryfolders"]
                del libfolders["contentstatsid"]
                # Search for Garry's Mod ID
                for lf in libfolders:
                    print("Searching in " + libfolders[lf]["path"] + "...")
                    if "4000" in libfolders[lf]["apps"]:
                        print("Found gmod app ID! Checking path...")
                        if os.path.isdir(
                            libfolders[lf]["path"]
                            + "\\steamapps\\common\\GarrysMod\\garrysmod"
                        ):
                            print("Found Garry's Mod!")
                            print(
                                libfolders[lf]["path"]
                                + "\\steamapps\\common\\GarrysMod\\garrysmod"
                            )
                            return (
                                libfolders[lf]["path"]
                                + "\\steamapps\\common\\GarrysMod\\garrysmod"
                            )
                        else:
                            print(
                                "Couldn't find Garry's Mod in this library folder despite it being listed in libraryfolders.vdf! Skipping..."
                            )
                raise FileNotFoundError("Could not find gmod in libraryfolders.vdf!")
            except (
                SyntaxError,
                AttributeError,
                FileNotFoundError,
                KeyError,
                WindowsError,
            ) as e:
                print("Could not parse libraryfolders.vdf\n" + str(e))
                print(
                    "Failed to parse libraryfolders.vdf. Trying steamapps/common where Steam is located..."
                )
                # Use the path to Steam as a guess
                if os.path.isdir(
                    reg_value[0] + "/steamapps/common/GarrysMod/garrysmod"
                ):
                    print("Found Garry's Mod!")
                    print(reg_value[0] + "/steamapps/common/GarrysMod/garrysmod")
                    return reg_value[0] + "/steamapps/common/GarrysMod/garrysmod"
                else:
                    raise FileNotFoundError(
                        "Could not find Garry's Mod in steamapps/common where Steam is located!"
                    )
        else:
            print(
                "Failed to find libraryfolders.vdf. Trying steamapps/common where Steam is located..."
            )
            # Use the path to Steam as a guess
            if os.path.isdir(reg_value[0] + "/steamapps/common/GarrysMod/garrysmod"):
                print("Found Garry's Mod!")
                print(reg_value[0] + "/steamapps/common/GarrysMod/garrysmod")
                return reg_value[0] + "/steamapps/common/GarrysMod/garrysmod"
            else:
                raise FileNotFoundError(
                    "Could not find Garry's Mod in steamapps/common where Steam is located!"
                )
    except (OSError, WindowsError, EnvironmentError, FileNotFoundError) as e:
        print("Failed to find/parse Steam data.\n" + str(e))
        print("Trying default programfiles (x86) path...")
        # Use the default programfiles (x86) path as a guess
        if os.path.isdir(
            "c:/program files (x86)/steam/steamapps/common/GarrysMod/garrysmod"
        ):
            print("Found Garry's Mod!")
            print("c:/program files (x86)/steam/steamapps/common/GarrysMod/garrysmod")
            return "c:/program files (x86)/steam/steamapps/common/GarrysMod/garrysmod"
        else:
            print("Not found in programfiles (x86), user must enter path manually.")
    return ""


def smart_path_select(title, pathvar):
    filename = filedialog.askdirectory(title=title)
    if not str(filename) == "()" and not str(filename) == "":
        pathvar.set(filename)


def start_download(
    master,
    frame,
    assetspath,
    username,
    password,
    successcallback,
    abortcallback,
):
    # TODO: Validate input HERE
    steamcmd_path = asyncio.run(check_scmd())
    if steamcmd_path == False or steamcmd_path == None:
        print("SteamCMD not found!")
        messagebox.showerror(
            "SteamCMD not found!", "SteamCMD not found! Please restart this program."
        )
        return
    get_css.main(
        master,
        frame,
        steamcmd_path,
        assetspath,
        username,
        password,
        successcallback,
        abortcallback,
    )


steamcmd_path = None


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master, background="black")
        self.master.title("gmodCSSDownloader - Main GUI")
        # self.master.iconbitmap("icon.ico")
        self.master.resizable(False, False)
        self.frame.pack()
        self.master.protocol("WM_DELETE_WINDOW", close_windows)
        steamcmd_path = asyncio.run(check_scmd())
        print("SteamCMD: " + str(steamcmd_path))
        if steamcmd_path == False:
            yn = messagebox.askyesno(
                "Not found",
                "SteamCMD not found in the PATH. Do you want to download it to the data directory?",
            )
            if yn:
                self.create_scmd_progress(
                    self.scmd_success_callback, self.scmd_abort_callback
                )
        self.gmodPathLabel = tk.Label(
            self.frame,
            text="garrysmod Path (not the game directory, but the asset directory inside it):",
            background="black",
            foreground="white",
        )
        self.gmodPathLabel.grid(row=0, column=0)
        self.gmodPathVar = tk.StringVar(self.frame, value=find_gmod())
        self.gmodPathEntry = tk.Entry(
            self.frame, width=65, textvariable=self.gmodPathVar
        )
        self.gmodPathEntry.grid(row=1, column=0)
        self.gmodPathButton = tk.Button(
            self.frame,
            text="Browse",
            command=lambda: smart_path_select(
                "Select garrysmod Path (not the game directory, but the asset directory inside it)",
                self.gmodPathVar,
            ),
        )
        self.gmodPathButton.grid(row=1, column=1)
        self.cssPathLabel = tk.Label(
            self.frame,
            text="Asset save path (moving, renaming, deleting etc. will break the assets)",
            background="black",
            foreground="white",
        )
        self.cssPathLabel.grid(row=2, column=0)
        self.cssPathVar = tk.StringVar(self.frame, value="./data/cstrike/")
        self.cssPathEntry = tk.Entry(self.frame, width=65, textvariable=self.cssPathVar)
        self.cssPathEntry.grid(row=3, column=0)
        self.cssPathButton = tk.Button(
            self.frame,
            text="Browse",
            command=lambda: smart_path_select(
                "Select asset save path (moving, renaming, deleting etc. will break the assets)",
                self.cssPathVar,
            ),
        )
        self.cssPathButton.grid(row=3, column=1)
        self.loginUserLabel = tk.Label(
            self.frame,
            text="Steam Username (it's recommended you leave this as the default)",
            background="black",
            foreground="white",
        )
        self.loginUserLabel.grid(row=4, column=0)
        self.loginUserVar = tk.StringVar(self.frame, value="anonymous")
        self.loginUserEntry = tk.Entry(
            self.frame, width=65, textvariable=self.loginUserVar
        )
        self.loginUserEntry.grid(row=5, column=0)
        self.loginPassLabel = tk.Label(
            self.frame,
            text="Steam Password (it's recommended you leave this as the default)",
            background="black",
            foreground="white",
        )
        self.loginPassLabel.grid(row=6, column=0)
        self.loginPassVar = tk.StringVar(self.frame, value="")
        self.loginPassEntry = tk.Entry(
            self.frame, width=65, textvariable=self.loginPassVar, show="*"
        )
        self.loginPassEntry.grid(row=7, column=0)
        self.startButton = tk.Button(
            self.frame,
            text="Start Download",
            command=lambda: self.create_css_progress(
                self.gmodPathVar.get(),
                self.cssPathVar.get(),
                self.loginUserVar.get(),
                self.loginPassVar.get(),
                self.css_success_callback,
                self.css_abort_callback,
            ),
        )
        self.startButton.grid(row=8, column=0)

    def create_scmd_progress(self, successcallback, abortcallback):
        self.master.withdraw()
        self.scmd_window = tk.Toplevel(self.master)
        self.app = SCMD_Progress(self.scmd_window, successcallback, abortcallback)

    def scmd_success_callback(self):
        self.scmd_window.destroy()
        self.master.deiconify()
        steamcmd_path = asyncio.run(check_scmd())  # check again after download
        print("SteamCMD: " + str(steamcmd_path))
        assert (
            steamcmd_path != False,
            "Something has gone terribly wrong in downloading SteamCMD! Please leave an issue on GitHub.",
        )

    def scmd_abort_callback(self):
        self.master.deiconify()
        messagebox.showerror("Aborted", "SteamCMD download was aborted!")

    def create_css_progress(
        self, gmodpath, assetspath, username, password, successcallback, abortcallback
    ):
        self.master.withdraw()
        self.css_window = tk.Toplevel(self.master)
        self.app = CSS_Progress(
            self.css_window,
            assetspath,
            username,
            password,
            successcallback,
            abortcallback,
        )

    def css_success_callback(self):
        self.master.deiconify()
        messagebox.showinfo("Success", "Downloaded CS:S assets successfully!")
        # TODO: go to write_mount

    def css_abort_callback(self):
        self.master.deiconify()
        messagebox.showinfo("Aborted", "CS:S assets download was aborted!")


class SCMD_Progress:
    def __init__(self, master, successcallback, abortcallback):
        self.master = master
        self.frame = tk.Frame(self.master, background="black")
        self.frame.pack()
        self.master.title("gmodCSSDownloader - SteamCMD Progress")
        get_scmd.main(self.master, self.frame, successcallback, abortcallback)


class CSS_Progress:
    def __init__(
        self,
        master,
        gmodpath,
        assetspath,
        username,
        password,
        successcallback,
        abortcallback,
    ):
        self.master = master
        self.frame = tk.Frame(self.master, background="black")
        self.frame.pack()
        self.master.title("gmodCSSDownloader - CS:S Progress")
        start_download(
            self.master,
            self.frame,
            gmodpath,
            assetspath,
            username,
            password,
            successcallback,
            abortcallback,
        )


def main():
    print("Launching GUI...")
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


if __name__ == "__main__":
    print("Launching GUI as debug...")
    main()
