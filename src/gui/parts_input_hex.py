import tkinter as tk
from tkinter import ttk
from typing import Any, Callable

from . import gui_common as gc


class HexInputWidget(ttk.Frame):
    def __init__(self, master: tk.Widget | None, initial_columns: int = 10, title_prefix: str = "", **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self.title_prefix = title_prefix
        self.labels: list[ttk.Label] = []
        self.entries: list[ttk.Entry] = []

        self.column_frame = ttk.Frame(self)
        self.column_frame.pack(side=tk.LEFT, padx=(0, 5), pady=5)

        for _ in range(initial_columns):
            self.add_column()

    def add_column(self) -> None:
        # 列タイトル設定
        col = len(self.entries)
        if self.title_prefix != "":
            title = f"{self.title_prefix}{col+1}"
        else:
            title = f"列{col+1}"

        # Labelを用意する
        label = ttk.Label(self.column_frame, text=title, font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        label.grid(row=0, column=col, padx=2, pady=1)
        self.labels.append(label)

        # 入力エリアを用意する
        entry = ttk.Entry(self.column_frame, width=3, font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        entry.grid(row=1, column=col, padx=2, pady=1)

        # イベントをバインドする
        self.bind_entry_events(entry, col)

        self.entries.append(entry)

    def update_arrow_handlers(self) -> None:
        for column, entry in enumerate(self.entries):
            self.bind_entry_events(entry, column)

    def bind_entry_events(self, entry: ttk.Entry, index: int) -> None:
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

        # 16進数以外の文字は入力を防ぐ
        char = event.char.upper()
        if char not in "0123456789ABCDEF":
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
            new_text = current_text[:start] + char + current_text[end:]
            if len(new_text) <= 2:
                event.widget.delete(0, tk.END)
                event.widget.insert(0, new_text)
                event.widget.icursor(start + 1)
            return "break"
        elif len(current_text) < 2:
            # 選択範囲がなく、2文字未満の場合は大文字に変換して挿入
            event.widget.insert(tk.INSERT, char)
            return "break"
        else:
            # 2文字以上の入力を防ぐ
            return "break"

    def is_control_key(self, event: tk.Event) -> bool:
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
    def get_raw_values(self) -> list[str]:
        """Entryの値をそのまま取得する

        Returns:
            list[str]: Entryウィジェットへ入力された文字列リスト
        """
        return [entry.get() for entry in self.entries]

    def get_values_csv(self) -> str:
        """Entryの値をcsv形式で取得する

        0文字の場合はそのまま
        1文字だけ入力されている場合は0埋めして2文字にする
        2文字の場合はそのまま

        Returns:
            str: カンマで結合した文字列
        """
        value_list = []
        # Entryから取得した文字列を加工する
        for value in self.get_raw_values():
            if len(value) == 1:
                # 1文字の領域を0埋めする
                padding_str = f"0{value}"
            else:
                # 2文字もしくは0文字の場合はそのまま
                padding_str = value
            value_list.append(padding_str)
        return ",".join(value_list)

    def set_values(self, values: list[str]) -> None:
        # 新しい値の数が現在の列数より多い場合、新しい列を追加
        for _ in range(len(values) - len(self.entries)):
            self.add_column()

        for entry, value in zip(self.entries, values):
            entry.delete(0, tk.END)
            entry.insert(0, value[:2])


# サンプル
if __name__ == "__main__":
    root = tk.Tk()
    root.title("16進数入力ウィジェット")

    test_frame = ttk.Frame(root)
    test_frame.pack()

    # デフォルトのタイトルを持つウィジェット
    hex_input1 = HexInputWidget(test_frame, initial_columns=5)
    hex_input1.pack(pady=10)

    # カスタムタイトル接頭辞を持つウィジェット
    hex_input2 = HexInputWidget(test_frame, initial_columns=5, title_prefix="FLD")
    hex_input2.pack(pady=10)

    # 値を取得するボタン
    def print_values() -> None:
        print("ウィジェット1の値:", hex_input1.get_raw_values())
        print("ウィジェット2の値:", hex_input2.get_raw_values())

    get_values_button = ttk.Button(root, text="値を取得", command=print_values)
    get_values_button.pack(pady=5)

    # 値をセットするボタン
    def set_sample_values() -> None:
        hex_input1.set_values(["A1", "B2", "C3", "D4", "E5", "F6", "G7"])
        hex_input2.set_values(["F6", "01", "23", "45", "67"])

    set_values_button = ttk.Button(root, text="サンプル値をセット", command=set_sample_values)
    set_values_button.pack(pady=5)

    root.mainloop()
