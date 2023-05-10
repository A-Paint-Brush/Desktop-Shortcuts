from PIL import Image, ImageTk, UnidentifiedImageError
from typing import *
import tkinter
import tkinter.font
import tkinter.messagebox as msg
import Config
import Global
import os.path
import subprocess
if TYPE_CHECKING:
    import Window


class Desktop(tkinter.Frame):
    def __init__(self, parent: "Window.MainWindow", script_path: str):
        super().__init__(parent)
        self.root = parent
        self.resolution = (0, 0)
        self.config = Config.Storage(script_path)
        self.root_dir = os.path.dirname(__file__)
        self.shortcuts: Tuple[Config.shortcuts, ...] = ()
        self.icon_images = []
        self.icon_handles = []
        self.window_size = []
        self.wallpaper_path = ""
        self.button_length = 0
        self.cell_margin = 0
        self.internal_padding = 0
        self.shortcut_font_size = 0
        self.context_font_size = 0
        self.resized_wallpaper = None
        self.context_menu = None
        self.load_xml(first_load=True)
        self.load_static_data(first_load=True)
        self.root.set_window_size(self.resolution)
        self.shortcut_font = tkinter.font.Font(family="Arial", size=self.shortcut_font_size, weight="normal")
        self.context_font = tkinter.font.Font(family="Arial", size=self.context_font_size, weight="normal")
        self.content_canvas = tkinter.Canvas(self, background="black", borderwidth=0, highlightthickness=0)
        self.content_canvas.pack(expand=True, fill="both")
        self.load_shortcut_data(first_load=True)
        self.render_surface(self.resolution, first_load=True)
        self.context_menu = ContextMenu(self.root, self.content_canvas, self.context_font,
                                        ["Refresh Shortcuts", "Quit"],
                                        [self.refresh_shortcuts, self.confirm_quit])
        self.root.bind("<Motion>", self.motion)
        self.root.bind("<ButtonRelease-1>", self.left_click)
        self.root.bind("<ButtonRelease-3>", self.context_menu.show_menu)

    def load_static_data(self, first_load: bool = False) -> None:
        try:
            self.resolution = tuple(int(i) for i in self.config.get_setting("resolution").split("x"))
            self.wallpaper_path = os.path.normpath(self.config.get_setting("wallpaper"))
            self.button_length = int(self.config.get_setting("button_length"))
            self.cell_margin = int(self.config.get_setting("cell_margin"))
            self.internal_padding = int(self.config.get_setting("internal_padding"))
            self.shortcut_font_size = int(self.config.get_setting("shortcut_font-size"))
            if first_load:
                self.context_font_size = int(self.config.get_setting("context_font-size"))
        except ValueError:
            message = "Malformed data found in the <settings> tag. Please ensure that you did not type in any " \
                      "non-numeric characters for settings that expect a numeric value."
            if first_load:
                msg.showerror("Fatal Error", message)
                raise SystemExit(1)
            else:
                self.root.after_idle(lambda: msg.showwarning("Warning", message))
        except AttributeError:
            message = "Missing tag in the <settings> tag. Please check that you have not accidentally deleted any " \
                      "tags that were originally in the file. If you do not know how to fix the file, delete it. The " \
                      "file will be recreated with default settings."
            if first_load:
                msg.showerror("Fatal Error", message)
                raise SystemExit(1)
            else:
                self.root.after_idle(lambda: msg.showwarning("Warning", message))
        if not first_load:
            self.shortcut_font = tkinter.font.Font(family="Arial", size=self.shortcut_font_size, weight="normal")

    def motion(self, event: tkinter.Event) -> None:
        collide = self.context_menu.update(event)
        for handle in self.content_canvas.find_withtag("shortcut_rect"):
            hit_box = self.content_canvas.coords(handle)
            if not collide and hit_box[0] <= event.x <= hit_box[2] and hit_box[1] <= event.y <= hit_box[3]:
                self.content_canvas.itemconfigure(handle, state="normal")
            else:
                self.content_canvas.itemconfigure(handle, state="hidden")

    def left_click(self, event: tkinter.Event) -> None:
        collide = self.context_menu.click(event)
        if not collide:
            command = None
            for index, handle in enumerate(self.icon_handles):
                hit_box = self.content_canvas.coords(handle)
                if hit_box[0] <= event.x <= hit_box[2] and hit_box[1] <= event.y <= hit_box[3]:
                    command = self.shortcuts[index].command
                    break
            if command is not None:
                try:
                    subprocess.Popen(command, shell=True)
                except OSError as e:
                    self.root.after_idle(lambda: msg.showwarning("Error",
                                                                 "Failed to execute command. The command failed with "
                                                                 "the below message:\n{}".format(e)))

    def refresh_shortcuts(self) -> None:
        self.load_shortcut_data()
        self.render_surface(self.resolution)

    def load_xml(self, first_load: bool = False) -> None:
        if self.config.init_xml_data():
            self.shortcuts = self.config.get_shortcut_data()
        else:
            if first_load:
                msg.showerror("Fatal Error", "Failed to load XML data.")
                raise SystemExit(1)
            else:
                self.root.after_idle(lambda: msg.showwarning("Warning", "Failed to reload XML data."))

    def load_shortcut_data(self, first_load: bool = False) -> None:
        if not first_load:
            self.load_xml()
            self.load_static_data()
            self.root.set_window_size(self.resolution)
        self.icon_images.clear()
        errors = 0
        for s in self.shortcuts:
            try:
                image = Image.open(os.path.expandvars(os.path.expanduser(os.path.normpath(s.icon_path))))\
                                  .convert("RGBA")
            except (OSError, UnidentifiedImageError):
                self.icon_images.append(None)
                errors += 1
            else:
                resized = image.resize(Global.resize_image(image.size,
                                                           (self.button_length - self.internal_padding * 2,) * 2))
                self.icon_images.append(ImageTk.PhotoImage(resized))
        if errors:
            self.root.after_idle(lambda: msg.showwarning("Warning",
                                                         "An error occurred while trying to load {} shortcut icon(s). "
                                                         "They will be left blank until the next time you refresh the "
                                                         "shortcuts.".format(errors)))

    def word_wrap_labels(self) -> List[List[str]]:
        return [Global.word_wrap_text(data.label_text,
                                      self.button_length - 2 * self.internal_padding,
                                      self.shortcut_font) for data in self.shortcuts]

    def render_surface(self, resolution: Tuple[int, int], first_load: bool = False, force_reload: bool = False) -> None:
        self.resolution = resolution
        self.content_canvas.delete("shortcut")
        self.icon_handles.clear()
        if force_reload:
            self.load_xml()
            self.load_static_data()
        try:
            wallpaper = Image.open(self.wallpaper_path)
        except (OSError, UnidentifiedImageError):
            message = "Failed to load the wallpaper image at {}".format(self.wallpaper_path)
            if first_load:
                msg.showerror("Fatal Error", message)
                raise SystemExit(1)
            else:
                self.root.after_idle(lambda: msg.showwarning("Warning", message))
        else:
            self.resized_wallpaper = ImageTk.PhotoImage(wallpaper.resize(Global.resize_image(wallpaper.size,
                                                                                             self.resolution)))
        self.content_canvas.create_image(resolution[0] / 2,
                                         resolution[1] / 2,
                                         image=self.resized_wallpaper,
                                         tags=("shortcut", "shortcut_wallpaper"))
        wrapped_labels = self.word_wrap_labels()
        max_label_height = max(len(lines) for lines in wrapped_labels) * self.shortcut_font.metrics("linespace")
        accumulated_width = self.cell_margin
        accumulated_height = self.cell_margin
        for index in range(len(self.shortcuts)):
            label_width = max(self.shortcut_font.measure(line) for line in wrapped_labels[index])
            if sum((accumulated_height, self.button_length, 2 * self.internal_padding, max_label_height,
                    self.cell_margin)) > self.resolution[1]:
                accumulated_width += self.button_length + self.cell_margin
                accumulated_height = self.cell_margin
            self.icon_handles.append(self.content_canvas.create_rectangle(accumulated_width,
                                                                          accumulated_height,
                                                                          accumulated_width + self.button_length,
                                                                          (accumulated_height
                                                                           + self.button_length
                                                                           + 2 * self.internal_padding
                                                                           + max_label_height),
                                                                          fill="#ffb6c1",
                                                                          tags=("shortcut", "shortcut_rect")))
            self.content_canvas.itemconfigure(self.icon_handles[-1], state="hidden")
            if self.icon_images[index] is not None:
                self.content_canvas.create_image(accumulated_width + self.internal_padding,
                                                 accumulated_height + self.internal_padding,
                                                 image=self.icon_images[index],
                                                 anchor="nw",
                                                 tags=("shortcut", "shortcut_icon"))
            self.content_canvas.create_text(accumulated_width + (self.button_length / 2 - label_width / 2),
                                            accumulated_height + self.button_length + self.internal_padding,
                                            text="\n".join(wrapped_labels[index]),
                                            anchor="nw",
                                            font=self.shortcut_font,
                                            fill="white",
                                            tags=("shortcut", "shortcut_label"))
            accumulated_height += sum((self.button_length, 2 * self.internal_padding, max_label_height,
                                       self.cell_margin))
        if self.context_menu is not None:
            self.context_menu.lift_to_top()

    def confirm_quit(self) -> None:
        if msg.askyesno("Really Quit?", "Are you sure you want to quit?"):
            self.root.destroy()


class ContextMenu:
    def __init__(self, root: "Window.MainWindow", parent: tkinter.Canvas, font: tkinter.font.Font, labels: List[str],
                 callbacks: List[Callable[[], None]]):
        self.display = True
        self.items = labels
        self.callbacks = callbacks
        self.button_handles = []
        self.coord_offsets = []
        self.offset_id = 0
        self.h_pad = 30
        self.v_pad = 5
        self.root = root
        self.parent = parent
        self.font = font
        self.width = max(self.font.measure(label) for label in self.items) + self.h_pad
        self.option_height = self.font.metrics("linespace") + self.v_pad
        self.height = self.option_height * len(self.items)
        self.content_frame = self.parent.create_rectangle(0, 0, self.width, self.height, fill="#f2f2f2",
                                                          tags="context_menu")
        for index, label in enumerate(self.items):
            self.coord_offsets.append((0, self.option_height * index, self.width,
                                       self.option_height * index + self.option_height))
            self.button_handles.append(self.parent.create_rectangle(*self.coord_offsets[self.offset_id], fill="#a1f3ff",
                                                                    tags=("context_menu", "button_rect",
                                                                          "menuitem{}".format(self.offset_id))))
            self.coord_offsets.append((self.h_pad / 2, self.option_height * index + self.v_pad / 2))
            self.parent.create_text(*self.coord_offsets[self.offset_id + 1], text=label, anchor="nw", font=self.font,
                                    fill="black", tags=("context_menu", "menuitem{}".format(self.offset_id + 1)))
            self.offset_id += 2
        self.hide_menu()

    def update(self, event: tkinter.Event) -> bool:
        if self.display:
            collide = False
            for handle in self.button_handles:
                hit_box = self.parent.coords(handle)
                if hit_box[0] <= event.x <= hit_box[2] and hit_box[1] <= event.y < hit_box[3]:
                    collide = True
                    self.parent.itemconfigure(handle, state="normal")
                else:
                    self.parent.itemconfigure(handle, state="hidden")
            return collide
        return False

    def click(self, event: tkinter.Event) -> bool:
        if self.display:
            frame_hit_box = self.parent.coords(self.content_frame)
            if frame_hit_box[0] <= event.x < frame_hit_box[2] and frame_hit_box[1] <= event.y < frame_hit_box[3]:
                collide = False
                for index, handle in enumerate(self.button_handles):
                    hit_box = self.parent.coords(handle)
                    if hit_box[0] <= event.x < hit_box[2] and hit_box[1] <= event.y < hit_box[3]:
                        collide = True
                        self.root.after_idle(self.callbacks[index])
                        self.hide_menu()
                        break
                return collide
            else:
                self.hide_menu()
                return False
        return False

    def show_menu(self, event: tkinter.Event) -> None:
        self.display = True
        for index, coord in enumerate(self.coord_offsets):
            handle = self.parent.find_withtag("menuitem{}".format(index))[0]
            if handle == self.content_frame:
                continue
            id_type = self.parent.type(handle)
            if id_type == "rectangle":
                self.parent.coords(handle, event.x + coord[0], event.y + coord[1], event.x + coord[2],
                                   event.y + coord[3])
            elif id_type == "text":
                self.parent.coords(handle, event.x + coord[0], event.y + coord[1])
                self.parent.itemconfigure(handle, state="normal")
        self.parent.coords(self.content_frame,
                           event.x,
                           event.y,
                           event.x + self.width,
                           event.y + self.height)
        self.parent.itemconfigure(self.content_frame, state="normal")

    def hide_menu(self) -> None:
        self.display = False
        for handle in self.parent.find_withtag("context_menu"):
            self.parent.itemconfigure(handle, state="hidden")

    def lift_to_top(self) -> None:
        self.parent.tag_raise(self.content_frame)
        for index in range(self.offset_id):
            handle = self.parent.find_withtag("menuitem{}".format(index))[0]
            self.parent.tag_raise(handle)
