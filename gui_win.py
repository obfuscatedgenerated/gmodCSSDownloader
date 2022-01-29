print("Launching GUI...")

import tkinter as tk
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


# check this before defferring to get_scmd_win
# print(asyncio.run(check_scmd()))
# if not false, then skip getting scmd


class MainWindow:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master, background="black")
        self.master.title("gmodCSSDownloader - Main GUI")
        # self.master.iconbitmap("icon.ico")
        self.frame.pack()

    def create_tips(self):
        self.new_window = tk.TopLevel(self.master)
        self.app = Tips(self.newWindow)


class Tips:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master, background="black")


def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()


# don't check for main, it's going to be called as a module
# if __name__ == "__main__":
#     main()

main()


# File select: Where to save?
# File select or perhaps auto detect: gmod path
# Optional input: use credentials? (default: anonymous)
