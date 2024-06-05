from server import Server
import tkinter


class ServerGUI:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.mainloop()


if __name__ == "__main__":
    ServerGUI()
    Server().start()
