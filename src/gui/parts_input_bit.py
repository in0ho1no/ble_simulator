import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from . import gui_common as gc


class BitInputWidget(ttk.Frame):
    MAX_FIELD = 8

    def __init__(self, master: tk.Widget | None, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.labels: list[ttk.Label] = []
        self.entries: list[ttk.Entry] = []

        self.column_frame = ttk.Frame(self)
        self.column_frame.pack(fill=tk.BOTH)

        # 8bit分の入力欄を用意する
        for _ in range(self.MAX_FIELD):
            self.add_column()

    def add_column(self) -> None:
        # 列タイトル設定
        col = len(self.entries)
        title = f"b{(self.MAX_FIELD - 1) - col}"

        # Labelを用意する
        label = ttk.Label(self.column_frame, text=title, font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        label.grid(row=0, column=col, padx=2, pady=1)
        self.labels.append(label)

        # 入力エリアを用意する
        entry = ttk.Entry(self.column_frame, width=2, font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        entry.grid(row=1, column=col, padx=2, pady=1)

        # イベントをバインドする
        self.bind_entry_events(entry, col)

        self.entries.append(entry)

    def bind_entry_events(self, entry: ttk.Entry, index: int) -> None:
        """Entry欄へのイベントを設定する

        Args:
            entry (ttk.Entry): イベントを設定したいEntryウィジェット
            index (int): _description_
        """
        entry.bind("<Key>", self.on_key)
        entry.bind("<Left>", self.create_arrow_handler(index, -1))
        entry.bind("<Right>", self.create_arrow_handler(index, 1))
        entry.bind("<BackSpace>", self.create_backspace_handler(index))

    # キー押下時
    def on_key(self, event: tk.Event) -> str | None:
        if not isinstance(event.widget, ttk.Entry):
            return None

        # Controlキーやショートカットキーの場合は処理をスキップ
        if self.is_control_key(event) or event.keysym in ("Left", "Right", "BackSpace", "Delete", "Tab"):
            return None

        # 2進数以外の文字は入力を防ぐ
        if event.char not in "01":
            return "break"

        # 選択範囲を取得
        try:
            selection_range = self.get_selection_range(event.widget)
        except tk.TclError:
            selection_range = None

        # 入力済み文字列を取得
        current_text = event.widget.get()
        if selection_range:
            # 選択範囲がある場合、その部分を新しい文字で置き換える
            start, end = selection_range
            new_text = current_text[:start] + event.char + current_text[end:]
            if len(new_text) <= 1:
                event.widget.delete(0, tk.END)
                event.widget.insert(0, new_text)
                event.widget.icursor(start + 1)
            return "break"
        elif len(current_text) < 1:
            # 選択範囲がなく、1文字未満の場合は挿入
            event.widget.insert(tk.INSERT, event.char)
            return "break"
        else:
            # 1文字以上の入力を防ぐ
            return "break"

    def is_control_key(self, event: tk.Event) -> bool:
        """controlキーの判定

        Args:
            event (tk.Event): 入力イベント

        Returns:
            bool: True: Controlキーである、 False: Controlキーではない
        """
        if isinstance(event.state, int):
            return bool(event.state & 0x4)
        elif isinstance(event.state, str):
            return "Control" in event.state

        return False

    def get_selection_range(self, entry: ttk.Entry) -> tuple | None:
        try:
            if entry.selection_present():
                return (entry.index(tk.SEL_FIRST), entry.index(tk.SEL_LAST))
        except tk.TclError:
            pass
        return None

    # 方向キー押下時
    def create_arrow_handler(self, index: int, direction: int) -> Callable[[tk.Event], str | None]:
        # tkinterの期待するイベントハンドラを渡すため、ラッピング
        def handler(event: tk.Event) -> str | None:
            return self.handle_arrow_key(event, index, direction)

        return handler

    def create_backspace_handler(self, index: int) -> Callable[[tk.Event], str | None]:
        def handler(event: tk.Event) -> str | None:
            return self.on_backspace(event, index)

        return handler

    def handle_arrow_key(self, event: tk.Event, current_index: int, direction: int) -> str | None:
        if not isinstance(event.widget, ttk.Entry):
            return None

        cursor_position = event.widget.index(tk.INSERT)
        current_text = event.widget.get()

        if direction == -1 and cursor_position == 0 and current_index > 0:
            # 左へ移動
            self.move_focus(current_index, -1)
            self.entries[current_index - 1].icursor(tk.END)
            return "break"
        elif direction == 1 and cursor_position == len(current_text) and current_index < len(self.entries) - 1:
            # 右へ移動
            self.move_focus(current_index, 1)
            self.entries[current_index + 1].icursor(0)
            return "break"
        return None

    def move_focus(self, current_index: int, direction: int) -> None:
        new_index = (current_index + direction) % len(self.entries)
        self.entries[new_index].focus()

    # バックスペース押下時
    def on_backspace(self, event: tk.Event, current_index: int) -> str | None:
        if not isinstance(event.widget, ttk.Entry):
            return None

        current_text = event.widget.get()
        cursor_position = event.widget.index(tk.INSERT)
        if current_text == "" and current_index > 0 and cursor_position == 0:
            self.move_focus(current_index, -1)
            self.entries[current_index - 1].icursor(tk.END)
            return "break"
        return None

    # フィールド制御
    def get_bin_str(self) -> str:
        """Entryの値を1文字ずつ結合した状態で取得する

        Returns:
            str: Entryウィジェットへ入力された文字を左から順に結合した文字列
        """
        bin_str = ""
        for entry in self.entries:
            value = entry.get()
            if 0 == len(value):
                bin_str += "0"
            else:
                bin_str += value

        return bin_str

    def get_hex_str(self) -> str:
        """Entryの値を16進数に変換して取得する

        Returns:
            str: 16進文字列
        """
        bin_str = self.get_bin_str()
        hex_int = int(bin_str, 2)
        hex_str = f"{hex_int:02X}"
        return hex_str
