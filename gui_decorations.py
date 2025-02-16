import tkinter as tk

# Константы оформления
BG_MAIN = "#f0f0f0"
BG_FRAME = "#e0e0e0"
HEADER_BG = BG_MAIN
HEADER_FG = "#333333"
HEADER_FONT = ("Helvetica", 16, "bold")
BUTTON_BG_SAVE = "#d9d9d9"
BUTTON_BG_START = "#a6e22e"
BUTTON_BG_STOP = "#f92672"
BUTTON_BG_UPDATE = "#d9d9d9"
LABEL_FONT = ("Helvetica", 10)
TOOLTIP_BG = "#ffffe0"
TOOLTIP_FONT = ("tahoma", "8", "normal")

# Класс для создания всплывающих подсказок
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
