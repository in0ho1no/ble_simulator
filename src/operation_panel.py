import asyncio
import concurrent.futures
import threading
import tkinter as tk
from tkinter import ttk

import gui.gui_common as gc
from ble_client import BleClient
from gui.parts_modern_button import ModernButton
from gui.parts_modern_combobox import ModernCombobox
from gui.parts_modern_label_frame import ModernLabelframe
from gui.parts_scrollable_hex_input import ScrollableHexInputWidget
from gui.window_log_viewer import LogViewer
from read_setting import SimSetting


class OperationPanel:
    def __init__(self, master: tk.Toplevel, sim_setting: SimSetting, log_viewer: LogViewer):
        self.master = master
        self.sim_setting = sim_setting
        self.log_viewer = log_viewer

        self.master.iconbitmap(gc.PATH_ICON)
        self.master.title(gc.TITLE_MAIN)
        self.master.geometry(f"+{gc.POS_MAIN_X}+{gc.POS_MAIN_Y}")
        self.master.resizable(False, False)

        # 非同期ループのためのイベントループ
        self.connection_task: None | concurrent.futures.Future = None
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.run_async_loop, daemon=True)
        self.thread.start()

        # BLEクライアント準備
        self.ble_client = BleClient(self.log_viewer)

        # プログレスバーの制御用変数
        self.progress_value = 0
        self.progress_running = False

        self.setup_ui()
        self.load_addresses(0)

    def run_async_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def setup_ui(self) -> None:
        # ボタンフレームの作成
        scan_button_frame = ModernLabelframe(self.master, text="アドバタイズパケット")
        # スキャン開始ボタン
        self.scan_button = ModernButton(scan_button_frame, text="スキャン開始", command=self.start_scan)
        # スキャン停止ボタン
        self.stop_button = ModernButton(scan_button_frame, text="スキャン停止", command=self.stop_scan, state="disabled")
        # 部品配置
        self.scan_button.pack(side=tk.LEFT, padx=(0, 5))
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))

        # BDアドレス設定フレーム
        bdadrs_setting_frame = ModernLabelframe(self.master, text="BDアドレス設定")
        # コンボボックス
        self.address_var = tk.StringVar()
        self.address_combo = ModernCombobox(bdadrs_setting_frame, textvariable=self.address_var)
        # 追加ボタン
        self.add_button = ModernButton(bdadrs_setting_frame, text="追加", command=self.add_address)
        # 削除ボタン
        self.remove_button = ModernButton(bdadrs_setting_frame, text="削除", command=self.remove_address)
        # 部品配置
        self.address_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.add_button.pack(side=tk.LEFT, padx=(0, 5))
        self.remove_button.pack(side=tk.LEFT, padx=(0, 5))

        # 指定アドレスと接続テストフレーム
        connection_test_frame = ModernLabelframe(self.master, text="指定アドレスと接続テスト")
        # テスト開始ボタン
        self.test_start_button = ModernButton(connection_test_frame, text="テスト開始", command=self.start_test)
        # テスト中断ボタン
        self.test_cancel_button = ModernButton(connection_test_frame, text="テスト中断", command=self.cancel_test, state="disabled")
        # データ読出ボタン
        self.read_data_button = ModernButton(connection_test_frame, text="データ読出", command=self.start_read_data)
        # 部品配置
        self.test_start_button.pack(side=tk.LEFT, padx=(0, 5))
        self.test_cancel_button.pack(side=tk.LEFT, padx=(0, 5))
        self.read_data_button.pack(side=tk.LEFT, padx=(0, 5))

        # コマンド種別指定
        type_frame = ModernLabelframe(self.master, text="コマンド種別指定")
        # タイプ設定
        type_label1 = ttk.Label(type_frame, text="Type1", font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        self.type_var1 = tk.StringVar()
        self.type_combo1 = ModernCombobox(type_frame, state="readonly", width=5, textvariable=self.type_var1, values=[f"{i:02X}" for i in range(16)])
        self.type_combo1.current(0)
        type_label1.grid(row=0, column=0)
        self.type_combo1.grid(row=1, column=0)
        # タイプ設定2
        type_label2 = ttk.Label(type_frame, text="Type2", font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        self.type_var2 = tk.StringVar()
        self.type_combo2 = ModernCombobox(type_frame, state="readonly", width=5, textvariable=self.type_var2, values=[f"{i:02X}" for i in range(32)])
        self.type_combo2.current(0)
        type_label2.grid(row=0, column=1)
        self.type_combo2.grid(row=1, column=1)
        # 種別設定1
        get_set_label1 = ttk.Label(type_frame, text="gs1", font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        self.get_set_var1 = tk.StringVar()
        self.get_set_combo1 = ModernCombobox(type_frame, state="readonly", width=5, textvariable=self.get_set_var1, values=["get", "set"])
        self.get_set_combo1.current(0)
        get_set_label1.grid(row=0, column=2)
        self.get_set_combo1.grid(row=1, column=2)
        # 種別設定2
        get_set_label2 = ttk.Label(type_frame, text="gs2", font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        self.get_set_var2 = tk.StringVar()
        self.get_set_combo2 = ModernCombobox(type_frame, state="readonly", width=5, textvariable=self.get_set_var2, values=["get2", "set2"])
        self.get_set_combo2.current(0)
        get_set_label2.grid(row=0, column=3)
        self.get_set_combo2.grid(row=1, column=3)
        # 種別設定3
        get_set_label3 = ttk.Label(type_frame, text="gs3", font=(gc.COMMON_FONT, gc.COMMON_FONT_SIZE))
        self.get_set_var3 = tk.StringVar()
        self.get_set_combo3 = ModernCombobox(type_frame, state="readonly", width=5, textvariable=self.get_set_var3, values=["A", "B", "C", "D"])
        self.get_set_combo3.current(0)
        get_set_label3.grid(row=0, column=4)
        self.get_set_combo3.grid(row=1, column=4)

        # 指定アドレスへ送信フレーム
        send_command_frame = ModernLabelframe(self.master, text="データ設定")
        # 値入力
        command_frame = ttk.Frame(send_command_frame)
        self.command_form = ScrollableHexInputWidget(command_frame, initial_columns=15, title_prefix="C", scrollable_height=50)
        self.command_form.pack(fill=tk.BOTH)

        command_button_frame = ttk.Frame(send_command_frame)
        # 確認ボタン
        self.check_button = ModernButton(command_button_frame, text="確認", command=self.check_command)
        self.check_button.pack(side=tk.LEFT, padx=(0, 5), pady=2)
        # 送信ボタン
        self.send_button = ModernButton(command_button_frame, text="送信", command=self.send_command)
        self.send_button.pack(side=tk.LEFT, pady=2)
        # 部品配置
        command_frame.pack(side=tk.TOP)
        command_button_frame.pack(side=tk.LEFT)

        # プログレスバーの追加
        progress_frame = tk.Frame(self.master)
        self.progress_bar = ttk.Progressbar(progress_frame, mode="determinate", length=100, maximum=100)
        # 部品配置
        self.progress_bar.pack(expand=True, fill=tk.X, padx=5)

        # ウィジェットの配置
        scan_button_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=5)
        bdadrs_setting_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=5)
        connection_test_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=5)
        type_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=5)
        send_command_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=10, pady=5)
        progress_frame.pack(side=tk.BOTTOM, expand=True, fill=tk.X, padx=5, pady=5)

    # BDアドレス管理
    def load_addresses(self, pos: int) -> None:
        addresses = self.sim_setting.get_bd_adrs()
        self.address_combo["values"] = addresses
        if pos < len(addresses):
            update_address = addresses[pos]
        else:
            update_address = ""
        self.address_combo.set(update_address)

    def add_address(self) -> None:
        new_address = self.address_var.get()
        if not new_address:
            self.log_viewer.add_log("エラー", "BDアドレスが入力されていません。")
            return

        if self.sim_setting.add_bd_adrs(new_address):
            # 追加したアドレスを表示する
            self.load_addresses(len(self.sim_setting.get_bd_adrs()) - 1)
            self.log_viewer.add_log("情報", f"BDアドレス '{new_address}' を追加しました。")
        else:
            self.log_viewer.add_log("エラー", "BDアドレスの追加に失敗しました。")

    def remove_address(self) -> None:
        address_to_remove = self.address_var.get()
        if not address_to_remove:
            self.log_viewer.add_log("エラー", "削除するBDアドレスを選択してください。")
            return

        if self.sim_setting.remove_bd_adrs(address_to_remove):
            self.load_addresses(0)
            self.log_viewer.add_log("情報", f"BDアドレス '{address_to_remove}' を削除しました。")
        else:
            self.log_viewer.add_log("エラー", "BDアドレスの削除に失敗しました。")

    # スキャン
    def start_scan(self) -> None:
        self.disable_buttons()
        self.stop_button.config(state="normal")
        self.start_progress()
        asyncio.run_coroutine_threadsafe(self.run_scanner(), self.loop)

    def stop_scan(self) -> None:
        self.log_viewer.add_log("情報", "スキャンを停止中...")
        self.ble_client.stop_scanner()
        self.stop_button.config(state="disabled")
        self.stop_progress()

    async def run_scanner(self) -> None:
        await self.ble_client.advertise_scanner()
        self.master.after(0, self.reset_buttons)
        self.master.after(0, self.stop_progress)

    # プログレスバー
    def start_progress(self) -> None:
        self.progress_running = True
        self.progress_value = 0
        self.update_progress()

    def stop_progress(self) -> None:
        self.progress_running = False
        self.progress_value = 0
        self.progress_bar["value"] = 0

    def update_progress(self) -> None:
        if self.progress_running:
            self.progress_value = (self.progress_value + 2) % 101  # 0-100の範囲で循環
            self.progress_bar["value"] = self.progress_value
            self.master.after(50, self.update_progress)

    # ボタン状態
    def reset_buttons(self) -> None:
        self.scan_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.test_start_button.config(state="normal")
        self.test_cancel_button.config(state="disabled")
        self.read_data_button.config(state="normal")
        self.send_button.config(state="normal")

    def disable_buttons(self) -> None:
        self.scan_button.config(state="disabled")
        self.test_start_button.config(state="disabled")
        self.read_data_button.config(state="disabled")
        self.send_button.config(state="disabled")

    # 接続テスト
    def start_test(self) -> None:
        if (self.connection_task is None) or (self.connection_task.done()):
            self.disable_buttons()
            self.test_cancel_button.config(state="normal")
            self.start_progress()
            self.connection_task = asyncio.run_coroutine_threadsafe(self.connection_test(), self.loop)

    def cancel_test(self) -> None:
        if (self.connection_task is not None) and (not self.connection_task.done()):
            self.connection_task.cancel()
            self.master.after(0, self.reset_buttons)
            self.master.after(0, self.stop_progress)

    async def connection_test(self) -> None:
        bd_adrs = self.address_combo.get()
        if bd_adrs is None:
            return False

        # 対象と接続
        self.log_viewer.add_log("情報", f"{bd_adrs}との接続テストを開始します。")
        await self.ble_client.test_client(bd_adrs)
        self.log_viewer.add_log("情報", f"{bd_adrs}との接続テストを終了します。")

        self.master.after(0, self.reset_buttons)
        self.master.after(0, self.stop_progress)

    def start_read_data(self) -> None:
        if (self.connection_task is None) or (self.connection_task.done()):
            self.disable_buttons()
            self.test_cancel_button.config(state="normal")
            self.start_progress()
            self.connection_task = asyncio.run_coroutine_threadsafe(self.read_data(), self.loop)

    async def read_data(self) -> None:
        bd_adrs = self.address_combo.get()
        if bd_adrs is None:
            return False

        # 対象と接続
        self.log_viewer.add_log("情報", f"{bd_adrs}からの情報取得を開始します。")
        await self.ble_client.read_client_data(bd_adrs)
        self.log_viewer.add_log("情報", f"{bd_adrs}からの情報取得を終了します。")

        self.master.after(0, self.reset_buttons)
        self.master.after(0, self.stop_progress)

    # 送信
    def check_command(self) -> None:
        type_setting = f"{self.type_combo1.get()},{self.type_combo2.get()},{self.get_set_combo1.get()},{self.get_set_combo2.current()},{self.get_set_combo3.current()}"
        data_setting = self.command_form.get_values_csv()
        # 末尾のカンマを除去する
        params = f"{type_setting},{data_setting}".rstrip(",")
        # 連続するカンマを0に置き換える
        params = params.replace(",,", ",00,")
        self.log_viewer.add_log("情報", f"{params}")

    def send_command(self) -> None:
        self.log_viewer.add_log("情報", "送信は未対応")
