import threading
import tkinter as tk


class RedSheet:
    def __init__(self, root):

        # locks
        self.locks = {
            'fullscreen': threading.Lock(),  # Used when fullscreen mode
            'minimize': threading.Lock(),    # Used when minimizing or restoring window
            'moving': threading.Lock()       # Used when dragging the window
        }

        # Window settings
        self.root=root
        self.root.title("RedSheet")
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.configure(bg="#FF0000")
        self.change_alpha(level=7.5)

        # Screen Information
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Change Window size and coordinates
        self.center_window(height_ratio=0.4, width_ratio=0.5)

        # Frame for resizing the four corners
        self.resizer_frames = []
        for relx, rely, anchor in [(0,0,"nw"), (1.0,0.0,"ne"), (0,1.0,"sw"), (1.0,1.0,"se")]:
            frame = tk.Frame(self.root, width=20, height=20)
            frame.config(bg=self.root.cget("background"))
            frame.place(relx=relx, rely=rely, anchor=anchor)
            frame.bind("<Button-1>", self.start_resize)
            frame.bind("<ButtonRelease-1>", self.close_resize)
            frame.bind("<B1-Motion>", self.resize)
            frame.bind("<Enter>", self.set_resizeing_cursor)
            frame.bind("<Leave>", self.set_default_cursor)
            self.resizer_frames.append([frame, relx, rely, anchor])

        # bind arrow keys to window
        arrow_keys = ["<Up>", "<Down>", "<Left>", "<Right>", "<Shift-Up>", "<Shift-Down>", "<Shift-Left>", "<Shift-Right>"]
        for key in arrow_keys:
            self.root.bind(key, self.on_arrow_key_pressed)

        # Change color
        self.root.bind("<KeyPress-r>", lambda event:self.change_color("red"))
        self.root.bind("<KeyPress-g>", lambda event:self.change_color("green"))
        self.root.bind("<KeyPress-b>", lambda event:self.change_color("blue"))

        # Bind for minimization
        self.root.bind("<KeyPress-h>", self.minimize_window)
        self.root.bind("<KeyPress-F4>", self.minimize_window)

        # bind as full screen
        self.root.bind("<KeyPress-f>", self.toggle_fullscreen)
        self.root.bind("<KeyPress-F11>", self.toggle_fullscreen)

        # bind for overrideredirect
        self.root.bind("<KeyPress-F10>", self.toggle_overrideredirect)

        # bind for close
        self.root.bind("<KeyPress-Escape>", lambda event: self.close_window())

        # bind to change transparency by pressing numeric keys
        for i in range(10):
            self.root.bind(f"<KeyPress-{i}>", lambda event, level=i: self.change_alpha(level=level))

        # bind to grab window and move position
        self.root.bind("<Button-1>", self.onMouseDown)
        self.root.bind("<ButtonRelease-1>", self.onMouseUp)
        self.root.bind("<B1-Motion>", self.onMouseMove)
        self.root.bind("<Motion>", self.onMove)

    # Minimize
    def minimize_window(self, *event):
        if self.locks["minimize"].locked():
            # Unminimize if already minimized

            # Return to the original based on the saved information.
            self.root.geometry(f"{self._tmp_minimize_original_width}x{self._tmp_minimize_original_height}+{self._tmp_minimize_original_x}+{self._tmp_minimize_original_y}")
            self.root.attributes("-alpha", self._tmp_minimize_original_alpha)
            self.root.config(bg=self._tmp_minimize_original_bg)

            self.show_all_resizer_frames()

            # lock release
            self.locks["minimize"].release()

        else:
            # Minimize if not minimized

            # lock acquire
            self.locks["minimize"].acquire()

            # Temporarily save window information
            self._tmp_minimize_original_width = self.root.winfo_width()
            self._tmp_minimize_original_height = self.root.winfo_height()
            self._tmp_minimize_original_alpha = self.root.attributes("-alpha")
            self._tmp_minimize_original_bg = self.root.cget("bg")
            self._tmp_minimize_original_x = self.root.winfo_x()
            self._tmp_minimize_original_y = self.root.winfo_y()

            # Minimize window
            self.root.geometry(f"100x100+2+2")
            self.root.attributes("-alpha", 0.5)

            self.hide_all_resizer_frames()

    # toggle fullscreen
    def toggle_fullscreen(self, event):
        if self.locks["fullscreen"].locked():
            # If already in full screen, deactivate full screen

            # Restore window size
            self.root.geometry(f"{self._tmp_fullscreen_original_width}x{self._tmp_fullscreen_original_height}+{self._tmp_fullscreen_original_x}+{self._tmp_fullscreen_original_y}")

            self.show_all_resizer_frames()

            # fullscreen_lock release
            self.locks["fullscreen"].release()

        else:
            # Full screen if not set to full screen

            # lock fullscreen
            self.locks["fullscreen"].acquire()

            # Temporarily save window information
            self._tmp_fullscreen_original_width = self.root.winfo_width()
            self._tmp_fullscreen_original_height = self.root.winfo_height()
            self._tmp_fullscreen_original_x = self.root.winfo_x()
            self._tmp_fullscreen_original_y = self.root.winfo_y()

            # Window full screen
            self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

            self.hide_all_resizer_frames()

    # toggle overrideredirect
    def toggle_overrideredirect(self, event):
        self.root.overrideredirect(not self.root.overrideredirect())

    # change color
    def change_color(self, color="#FF0000"):
        self.root.configure(bg=color)
        self.show_all_resizer_frames()

    # change Transparency
    def change_alpha(self, level=7, *args):
        if not self.locks["minimize"].locked():
            if level == 0:
                self.change_alpha() # default
            elif isinstance(level, (int, float)):
                alpha=level/10
                self.root.attributes("-alpha", alpha)

    # For moving the four-way controller
    def on_arrow_key_pressed(self, event):
        # Get coordinates of current window
        x, y = self.root.winfo_x(), self.root.winfo_y()

        # normal movement
        MOVE_AMOUNT = 25
        # micro movement with shift
        MICRO_MOVE_AMOUNT = 3

        if event.keysym in ['Up']:
            y -= MOVE_AMOUNT if not event.state & 0x0001 else MICRO_MOVE_AMOUNT
        elif event.keysym in ['Down']:
            y += MOVE_AMOUNT if not event.state & 0x0001 else MICRO_MOVE_AMOUNT
        elif event.keysym in ['Left']:
            x -= MOVE_AMOUNT if not event.state & 0x0001 else MICRO_MOVE_AMOUNT
        elif event.keysym in ['Right']:
            x += MOVE_AMOUNT if not event.state & 0x0001 else MICRO_MOVE_AMOUNT

        # Adapting to Movement
        self.root.geometry(f"+{x}+{y}")

    # For grabbing and moving windows
    def onMouseDown(self, event):
        if self.locks["moving"].locked() or self.locks["fullscreen"].locked():
            return

        self.root.config(cursor="fleur")

        self.root.startX = event.x
        self.root.startY = event.y

    # For grabbing and moving windows
    def onMouseMove(self, event):
        if self.locks["moving"].locked() or self.locks["fullscreen"].locked():
            return
        x = self.root.winfo_x() - self.root.startX + event.x
        y = self.root.winfo_y() - self.root.startY + event.y
        self.root.geometry("+%s+%s" % (x , y))

    # For grabbing and moving windows
    def onMouseUp(self, event):
        self.root.config(cursor="")

    # Release minimized state with mouse hover
    def onMove(self, event):
        if self.locks["minimize"].locked():
            self.minimize_window()
            self.root.focus_force()

    # hide resizer
    def hide_all_resizer_frames(self):
        for frame, relx, rely, anchor in self.resizer_frames:
            frame.place_forget()

    # show resizer
    def show_all_resizer_frames(self):
        for frame, relx, rely, anchor in self.resizer_frames:
            frame.place(relx=relx, rely=rely, anchor=anchor)
            frame.config(bg=self.root.cget("background"))

    # For resizing at the four corners
    def start_resize(self, event):
        self.locks["moving"].acquire()

        # Remember where you clicked
        self.resize_start_x = event.x
        self.resize_start_y = event.y

    # For resizing at the four corners
    def close_resize(self, event):
        self.locks["moving"].release()

    # For resizing at the four corners
    def resize(self, event):
        # Minimum window size
        MIN_SIZE = 50

        # place_info
        place_info=event.widget.place_info()

        # Calculate the amount of movement relative to the clicked position
        delta_x = event.x - self.resize_start_x
        delta_y = event.y - self.resize_start_y

        # Get the current window size
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = self.root.winfo_x()
        y = self.root.winfo_y()

        if place_info["anchor"]=="nw":

            # Change size and position
            width -= delta_x
            height -= delta_y
            x += delta_x
            y += delta_y

            if width <= MIN_SIZE:
                width = MIN_SIZE
                x -= delta_x
            if height <= MIN_SIZE:
                height = MIN_SIZE
                y -= delta_y

            # Change window size and position
            self.root.geometry(f"{width}x{height}+{x}+{y}")

        elif place_info["anchor"]=="ne":
            # Change size
            width += delta_x
            height -= delta_y

            y += delta_y

            # Adjust the size so that it is not less than 50px
            if width <= MIN_SIZE:
                width = MIN_SIZE
                x -= MIN_SIZE - width
            if height <= MIN_SIZE:
                height = MIN_SIZE
                y-=delta_y

            # Resize the window
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        elif place_info["anchor"]=="sw":
            # Change size
            width -= delta_x
            height += delta_y

            x += delta_x

            # Adjust the size so that it is not less than 50px
            if width <= MIN_SIZE:
                width = MIN_SIZE
                x -= delta_x
            if height <= MIN_SIZE:
                height = MIN_SIZE
                y -= MIN_SIZE - height

            # Resize the window
            self.root.geometry(f"{width}x{height}+{x}+{y}")

        elif place_info["anchor"]=="se":
            # Change size
            width += delta_x
            height += delta_y

            # Adjust the size so that it is not less than 50px
            if width <= MIN_SIZE:
                width = MIN_SIZE
            if height <= MIN_SIZE:
                height = MIN_SIZE

            # Resize the window
            self.root.geometry(f"{width}x{height}")

    # Cursor Default
    def set_default_cursor(self, event):
        self.root.config(cursor="")

    # Cursor Resize at four corners
    def set_resizeing_cursor(self, event):
        place_info=event.widget.place_info()

        if place_info["anchor"]=="nw":
            self.root.config(cursor="size_nw_se")
        elif place_info["anchor"]=="ne":
            self.root.config(cursor="size_ne_sw")
        elif place_info["anchor"]=="sw":
            self.root.config(cursor="size_ne_sw")
        elif place_info["anchor"]=="se":
            self.root.config(cursor="size_nw_se")

    # center window
    def center_window(self, width_ratio=0.3, height_ratio=0.2):
        # Calculate window size based on ratio
        window_width = int(self.screen_width * width_ratio)
        window_height = int(self.screen_height * height_ratio)

        # Calculate coordinates for centering
        x = (self.screen_width - window_width) // 2
        y = (self.screen_height - window_height) // 2

        # Set the geometry
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # close
    def close_window(self, *args):
        self.root.destroy()

    # run
    def run(self):
        self.root.mainloop()


def main():
    root = tk.Tk()
    app = RedSheet(root)
    root.mainloop()


if __name__ == "__main__":
    main()
