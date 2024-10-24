import tkinter as tk
from typing import Callable


class MenuBuilder:
    """メニューバーの構築を担当するクラス"""

    def __init__(self, root: tk.Tk):
        self.menubar = tk.Menu(root)
        self.menu = tk.Menu(self.menubar, tearoff=0)

    def build_menu(self, menu_label: str, create_window_callback: Callable) -> None:
        """メニューの構築"""
        self.menubar.add_cascade(label="メニュー", menu=self.menu)
        self.menu.add_command(label=menu_label, command=create_window_callback)

    def get_menubar(self) -> tk.Menu:
        """構築したメニューバーを返す"""
        return self.menubar
