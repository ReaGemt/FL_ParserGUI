import tkinter as tk

# Обновлённые стили оформления
BG_MAIN = "#ffffff"
BG_FRAME = "#f7f7f7"
HEADER_BG = "#282c34"
HEADER_FG = "#61dafb"
HEADER_FONT = ("Segoe UI", 18, "bold")

BUTTON_BG_SAVE = "#61dafb"
BUTTON_BG_START = "#28a745"
BUTTON_BG_STOP = "#dc3545"
BUTTON_BG_UPDATE = "#ffc107"

LABEL_FONT = ("Segoe UI", 10)
TOOLTIP_BG = "#ffffcc"
TOOLTIP_FONT = ("Segoe UI", 9)


class CreateToolTip(object):
    """
    Создаёт всплывающую подсказку для заданного виджета.
    """
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        widget.bind("<Enter>", self.enter)
        widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        _id = self.id
        self.id = None
        if _id:
            self.widget.after_cancel(_id)

    def showtip(self, event=None):
        x, y, cx, cy = self.widget.bbox("insert") or (0,0,0,0)
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background=TOOLTIP_BG, relief=tk.SOLID, borderwidth=1,
                         font=TOOLTIP_FONT)
        label.pack(ipadx=1)

    def hidetip(self):
        if self.tipwindow:
            self.tipwindow.destroy()
        self.tipwindow = None