"""
ScreenPen for Windows - Lightweight Transparent Overlay Screen Annotation Tool
Runs natively on Windows 10/11 using standard Python with Tkinter.
Supports Pen, Highlighter, Eraser, Spotlight, Clear, Undo, and Keyboard Hotkeys.
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox


PANEL_BG = "#282b31"
PANEL_BORDER = "#686d77"
BUTTON_BG = "#343842"
TEXT_COLOR = "#f3f4f6"
MUTED_COLOR = "#b8bfca"
ACCENT_COLOR = "#ffe08a"
PEN_COLORS = ("#ff648c", "#ff614d", "#4cb8ff", "#4addbc", "#a887ff", "#31416a")
HIGHLIGHTER_COLORS = ("#ffe35a", "#ffb461", "#7ddfff", "#80eea1", "#c7a6ff", "#ff91c1")


class ScreenPenWindows:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ScreenPen Overlay")
        
        # Transparent, borderless, always on top, full screen
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.0) # start transparent/invisible
        
        # Windows-specific transparent color keying
        self.trans_color = "#000001"
        try:
            self.root.wm_attributes("-transparentcolor", self.trans_color)
        except Exception:
            pass

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Canvas for drawing
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            bg=self.trans_color,
            highlightthickness=0,
            cursor="crosshair"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Drawing state
        self.current_tool = "pen"  # pen, highlighter, eraser, spotlight
        self.pen_color = PEN_COLORS[1]
        self.highlighter_color = HIGHLIGHTER_COLORS[0]
        self.pen_width = 4
        self.highlighter_width = 18
        self.eraser_radius = 24
        self.is_active = False

        self.last_x = None
        self.last_y = None
        self.strokes = []  # list of stroke item IDs for undo
        self.current_stroke_items = []
        self.spotlight_item = None

        # Windows passes clicks through the color-keyed canvas background.
        # A nearly transparent window receives input above the drawing canvas.
        self.input_overlay = tk.Toplevel(self.root, bg="black")
        self.input_overlay.withdraw()
        self.input_overlay.overrideredirect(True)
        self.input_overlay.attributes("-topmost", True)
        self.input_overlay.attributes("-alpha", 0.01)
        self.input_overlay.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        self.input_overlay.bind("<Button-1>", self.on_mouse_down)
        self.input_overlay.bind("<B1-Motion>", self.on_mouse_drag)
        self.input_overlay.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.input_overlay.bind("<Motion>", self.on_mouse_move)
        self.input_overlay.bind("<Button-3>", lambda e: self.deactivate())

        self.setup_toolbar()
        for window in (self.root, self.input_overlay, self.toolbar):
            window.bind("<Escape>", lambda e: self.deactivate())
            window.bind("<Control-Alt-Key-1>", lambda e: self.activate_tool("pen"))
            window.bind("<Control-Alt-Key-2>", lambda e: self.activate_tool("highlighter"))
            window.bind("<Control-Alt-Key-3>", lambda e: self.activate_tool("spotlight"))
            window.bind("<Control-Alt-Key-5>", lambda e: self.activate_tool("eraser"))
            window.bind("<Control-Alt-grave>", lambda e: self.clear_all())
            window.bind("<Control-z>", lambda e: self.undo())
            window.bind("<Control-Z>", lambda e: self.undo())
            window.bind("<Control-Alt-Key-o>", lambda e: self.toggle_help())

    def setup_toolbar(self):
        self.toolbar = tk.Toplevel(self.root)
        self.toolbar.title("ScreenPen Toolbar")
        self.toolbar.attributes("-topmost", True)
        self.toolbar.overrideredirect(True)
        self.toolbar.configure(bg=self.trans_color)
        self.toolbar.wm_attributes("-transparentcolor", self.trans_color)

        self.help_card, help_content = self.make_card()
        self.tools_card, tools = self.make_card()
        self.help_card.pack(fill=tk.X, pady=(0, 8))
        self.tools_card.pack(fill=tk.X)

        self.panel_title(help_content, "ScreenPen 단축키").pack(anchor="w", pady=(0, 5))
        shortcuts = tk.Frame(help_content, bg=PANEL_BG)
        shortcuts.pack(fill=tk.X)
        for row, (keys, action) in enumerate((
            ("Ctrl+Alt+1 / 2", "펜 / 형광펜"),
            ("Ctrl+Alt+3 / 5", "스포트 / 지우개"),
            ("Ctrl+Z", "되돌리기"),
            ("Ctrl+Alt+`", "전체 지우기"),
            ("Ctrl+Alt+O", "단축키 안내 켜기·끄기"),
            ("Esc / 우클릭", "도구 끄기"),
            ("Win++ / Win+Esc", "돋보기 켜기 / 끄기"),
        )):
            tk.Label(shortcuts, text=keys, bg=PANEL_BG, fg=TEXT_COLOR, font=("Segoe UI", 9)).grid(
                row=row, column=0, sticky="w", padx=(0, 12)
            )
            tk.Label(shortcuts, text=action, bg=PANEL_BG, fg=MUTED_COLOR, font=("Malgun Gothic", 9)).grid(
                row=row, column=1, sticky="w"
            )

        header = tk.Frame(tools, bg=PANEL_BG)
        header.pack(fill=tk.X, pady=(0, 7))
        self.panel_title(header, "ScreenPen 도구").pack(side=tk.LEFT)
        self.panel_button(header, "×", self.quit_app).pack(side=tk.RIGHT)
        self.help_button = self.panel_button(header, "?", self.toggle_help)
        self.help_button.pack(side=tk.RIGHT, padx=(5, 4))
        self.mode_label = tk.Label(header, bg=PANEL_BG, fg=MUTED_COLOR, font=("Malgun Gothic", 8))
        self.mode_label.pack(side=tk.RIGHT)

        grid = tk.Frame(tools, bg=PANEL_BG)
        grid.pack(fill=tk.X)
        self.tool_buttons = {}
        for index, (name, label, command) in enumerate((
            ("pen", "✎  펜", lambda: self.activate_tool("pen")),
            ("highlighter", "▰  형광펜", lambda: self.activate_tool("highlighter")),
            ("eraser", "◇  지우개", lambda: self.activate_tool("eraser")),
            ("spotlight", "◎  스포트", lambda: self.activate_tool("spotlight")),
            (None, "⊕  화면 확대", self.open_magnifier),
            ("off", "○  도구 끄기", self.deactivate),
            (None, "↶  되돌리기", self.undo),
            (None, "×  전체 지우기", self.clear_all),
            (None, "⚙  확대 설정", self.open_magnifier_settings),
        )):
            row, column = divmod(index, 3)
            button = self.panel_button(grid, label, command)
            button.grid(row=row, column=column, sticky="ew", padx=2, pady=2, ipady=2)
            grid.columnconfigure(column, weight=1, uniform="tool")
            if name is not None:
                self.tool_buttons[name] = button

        palette = tk.Frame(tools, bg=PANEL_BG)
        palette.pack(fill=tk.X, pady=(7, 0))
        self.color_label = tk.Label(palette, bg=PANEL_BG, fg=MUTED_COLOR, font=("Malgun Gothic", 9))
        self.color_label.pack(side=tk.LEFT, padx=(2, 8))
        self.swatches = tk.Canvas(palette, width=168, height=28, bg=PANEL_BG, highlightthickness=0)
        self.swatches.pack(side=tk.RIGHT)
        self.color_items = []
        for index in range(len(PEN_COLORS)):
            x = 5 + 27 * index
            item = self.swatches.create_oval(x, 5, x + 18, 23)
            self.color_items.append(item)
            self.swatches.tag_bind(item, "<Button-1>", lambda event, index=index: self.select_color(index))

        self.refresh_toolbar()
        self.toolbar.update_idletasks()
        width = max(help_content.winfo_reqwidth(), tools.winfo_reqwidth()) + 20
        for card, content in ((self.help_card, help_content), (self.tools_card, tools)):
            card.configure(width=width, height=content.winfo_reqheight() + 16)
        self.toolbar.update_idletasks()
        self.move_toolbar((self.screen_width - width) // 2, self.screen_height - self.toolbar.winfo_height() - 64)
        self.toolbar.update_idletasks()

    def make_card(self):
        card = tk.Canvas(self.toolbar, bg=self.trans_color, highlightthickness=0)
        content = tk.Frame(card, bg=PANEL_BG)
        panel = card.create_polygon(0, 0, 0, 0, 0, 0, fill=PANEL_BG, outline=PANEL_BORDER, smooth=True)
        body = card.create_window(10, 8, window=content, anchor="nw")

        def resize(event):
            w, h, r = event.width - 2, event.height - 2, 13
            card.coords(panel, r, 1, w-r, 1, w, 1, w, r, w, h-r, w, h,
                        w-r, h, r, h, 1, h, 1, h-r, 1, r, 1, 1)
            card.itemconfigure(body, width=event.width - 20)

        card.bind("<Configure>", resize)
        return card, content

    def panel_title(self, parent, text):
        title = tk.Label(parent, text=text, bg=PANEL_BG, fg=TEXT_COLOR, font=("Malgun Gothic", 10, "bold"),
                         cursor="fleur")
        title.bind("<ButtonPress-1>", self.start_move_toolbar)
        title.bind("<B1-Motion>", self.do_move_toolbar)
        return title

    def panel_button(self, parent, label, command):
        return tk.Button(parent, text=label, command=command, font=("Malgun Gothic", 9), bg=BUTTON_BG,
                         fg=TEXT_COLOR, activebackground="#4b5261", activeforeground=TEXT_COLOR,
                         relief="flat", bd=0, padx=5, pady=3, highlightthickness=1,
                         highlightbackground=PANEL_BORDER, highlightcolor=ACCENT_COLOR, cursor="hand2")

    def refresh_toolbar(self):
        active_tool = self.current_tool if self.is_active else "off"
        for name, button in self.tool_buttons.items():
            selected = name == active_tool
            button.configure(bg="#4b4435" if selected else BUTTON_BG,
                             fg=ACCENT_COLOR if selected else TEXT_COLOR,
                             highlightbackground=ACCENT_COLOR if selected else PANEL_BORDER)
        self.mode_label.configure(text="필기 모드" if self.is_active else "마우스 모드")

        highlighter = self.current_tool == "highlighter"
        self.color_label.configure(text="형광 색상" if highlighter else "펜 색상")
        colors = HIGHLIGHTER_COLORS if highlighter else PEN_COLORS
        current_color = self.highlighter_color if highlighter else self.pen_color
        for item, color in zip(self.color_items, colors):
            selected = color == current_color
            self.swatches.itemconfigure(item, fill=color, outline=ACCENT_COLOR if selected else PANEL_BORDER,
                                        width=3 if selected else 1)

    def select_color(self, index):
        if self.current_tool == "highlighter":
            self.highlighter_color = HIGHLIGHTER_COLORS[index]
            self.activate_tool("highlighter")
        else:
            self.pen_color = PEN_COLORS[index]
            self.activate_tool("pen")

    def toggle_help(self):
        bottom = self.toolbar.winfo_y() + self.toolbar.winfo_height()
        if self.help_card.winfo_manager():
            self.help_card.pack_forget()
        else:
            self.help_card.pack(before=self.tools_card, fill=tk.X, pady=(0, 8))
        self.toolbar.update_idletasks()
        self.move_toolbar(self.toolbar.winfo_x(), bottom - self.toolbar.winfo_height())

    def open_magnifier(self):
        self.open_windows_tool(os.path.join(os.environ["SystemRoot"], "System32", "Magnify.exe"))

    def open_magnifier_settings(self):
        self.open_windows_tool("ms-settings:easeofaccess-magnifier")

    def open_windows_tool(self, target):
        self.deactivate()
        try:
            os.startfile(target)
        except OSError:
            messagebox.showerror("ScreenPen", "Windows 돋보기를 열 수 없습니다.", parent=self.toolbar)

    def start_move_toolbar(self, event):
        self._tb_x = event.x_root - self.toolbar.winfo_x()
        self._tb_y = event.y_root - self.toolbar.winfo_y()

    def do_move_toolbar(self, event):
        self.move_toolbar(event.x_root - self._tb_x, event.y_root - self._tb_y)

    def move_toolbar(self, x, y):
        x = max(0, min(x, self.screen_width - self.toolbar.winfo_width()))
        y = max(0, min(y, self.screen_height - self.toolbar.winfo_height()))
        self.toolbar.geometry(f"+{x}+{y}")

    def activate_tool(self, tool):
        self.current_tool = tool
        self.is_active = True
        self.root.attributes("-alpha", 1.0)
        self.root.lift()
        self.input_overlay.deiconify()
        self.input_overlay.lift()
        self.input_overlay.focus_force()
        self.toolbar.lift()

        self.refresh_toolbar()
        self.input_overlay.configure(cursor="none" if tool == "spotlight" else "crosshair")

    def deactivate(self):
        self.is_active = False
        self.input_overlay.withdraw()
        if self.spotlight_item:
            self.canvas.delete(self.spotlight_item)
            self.spotlight_item = None
        self.root.attributes("-alpha", 0.0)
        self.refresh_toolbar()

    def on_mouse_down(self, event):
        if not self.is_active:
            return
        self.last_x = event.x
        self.last_y = event.y
        self.current_stroke_items = []

        if self.current_tool == "eraser":
            self.erase_at(event.x, event.y)

    def on_mouse_drag(self, event):
        if not self.is_active:
            return
        if self.last_x is None:
            self.last_x = event.x
            self.last_y = event.y
            return

        if self.current_tool == "pen":
            line = self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                fill=self.pen_color, width=self.pen_width,
                capstyle=tk.ROUND, joinstyle=tk.ROUND, smooth=True
            )
            self.current_stroke_items.append(line)
        elif self.current_tool == "highlighter":
            line = self.canvas.create_line(
                self.last_x, self.last_y, event.x, event.y,
                fill=self.highlighter_color, width=self.highlighter_width,
                capstyle=tk.ROUND, joinstyle=tk.ROUND, smooth=True
            )
            self.current_stroke_items.append(line)
        elif self.current_tool == "eraser":
            self.erase_at(event.x, event.y)

        self.last_x = event.x
        self.last_y = event.y

    def on_mouse_up(self, event):
        if self.current_stroke_items:
            self.strokes.append(self.current_stroke_items)
            self.current_stroke_items = []
        self.last_x = None
        self.last_y = None

    def on_mouse_move(self, event):
        if self.current_tool == "spotlight" and self.is_active:
            if self.spotlight_item:
                self.canvas.delete(self.spotlight_item)
            r = 75
            self.spotlight_item = self.canvas.create_oval(
                event.x - r, event.y - r, event.x + r, event.y + r,
                outline="#feca57", width=3
            )

    def erase_at(self, x, y):
        r = self.eraser_radius
        overlapping = self.canvas.find_overlapping(x - r, y - r, x + r, y + r)
        for item in overlapping:
            if item != self.spotlight_item:
                self.canvas.delete(item)
                for stroke in self.strokes:
                    if item in stroke:
                        stroke.remove(item)

    def undo(self):
        if self.strokes:
            last_stroke = self.strokes.pop()
            for item in last_stroke:
                self.canvas.delete(item)

    def clear_all(self):
        self.canvas.delete("all")
        self.strokes.clear()
        self.spotlight_item = None

    def quit_app(self):
        self.root.destroy()
        sys.exit(0)

    def run(self):
        self.activate_tool("pen")
        self.root.mainloop()

if __name__ == "__main__":
    app = ScreenPenWindows()
    app.run()
