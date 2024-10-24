import tkinter as tk
from tkinter import ttk
from typing import Any

from .parts_input_hex import HexInputWidget
from .parts_modern_button import ModernButton
from .parts_scrollable_frame import ScrollableFrame


class ScrollableHexInputWidget(ttk.Frame):
    def __init__(self, master: ttk.Frame, initial_columns: int = 10, title_prefix: str = "", scrollable_height: int = 200, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)

        self.button_frame = ttk.Frame(master)
        self.button_frame.pack(side=tk.TOP, fill=tk.X)

        self.add_column_button = ModernButton(self.button_frame, text="列を追加", command=self.add_column)
        self.add_column_button.pack(side=tk.LEFT)

        self.scrollable_frame = ScrollableFrame(master, vertical_scroll=False, horizontal_scroll=True, height=scrollable_height)
        self.scrollable_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.hex_input = HexInputWidget(self.scrollable_frame.scrolled_frame, initial_columns=initial_columns, title_prefix=title_prefix)
        self.hex_input.pack(expand=True, fill=tk.BOTH)

    def add_column(self) -> None:
        self.hex_input.add_column()
        self.redraw()

    def redraw(self) -> None:
        self.scrollable_frame.force_update()
        self.scrollable_frame.force_update()
        self.scrollable_frame.canvas.xview_moveto(1)

    def get_raw_values(self) -> list[str]:
        return self.hex_input.get_raw_values()

    def get_values_csv(self) -> str:
        return self.hex_input.get_values_csv()

    def set_values(self, values: list[str]) -> None:
        self.hex_input.set_values(values)
        self.redraw()
