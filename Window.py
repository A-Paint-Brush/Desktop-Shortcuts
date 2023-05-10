from typing import *
import Frames
import tkinter


class MainWindow(tkinter.Tk):
    def __init__(self, script_path: str):
        super().__init__()
        self.resolution = (0, 0)
        self.geometry_string = ""
        self.offset_x, self.offset_y = self.get_offset()
        self.content_frame = None
        self.title("Desktop")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        self.content_frame = Frames.Desktop(self, script_path)
        self.content_frame.pack(expand=True, fill="both")
        self.lock_window()
        self.mainloop()

    def get_offset(self) -> Tuple[int, int]:
        self.geometry("10x10+0+0")
        self.update()
        return -self.winfo_rootx(), -self.winfo_rooty()

    def set_window_size(self, size: Tuple[int, int]) -> None:
        self.resolution = size
        self.geometry_string = "{}x{}+{}+{}".format(size[0], size[1], self.offset_x, self.offset_y)

    def lock_window(self) -> None:
        if self.state() != "normal" or not self.winfo_ismapped():
            self.deiconify()
            self.attributes("-topmost", True)
            self.attributes("-topmost", False)
        if self.geometry() != self.geometry_string:
            self.geometry(self.geometry_string)
        self.after(50, self.lock_window)
