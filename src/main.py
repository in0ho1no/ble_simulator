import tkinter as tk

import define_main as dm
from gui.menu_builder import MenuBuilder
from gui.window_bytes_operation import ByteWindowManager
from gui.window_log_viewer import LogViewer
from operation_panel import OperationPanel
from read_setting import SimSetting


class BLEManager:
    def __init__(self) -> None:
        self.root = tk.Tk()
        # 不要なメインウィンドウを非表示にする
        self.root.withdraw()

        # 基本コンポーネントの初期化
        self.sim_setting = SimSetting(dm.PATH_SETTING)
        self._init_log_viewer()
        self._init_operation_panel()

        # Byte演算ウィンドウ管理の初期化
        self.byte_window_manager = ByteWindowManager(self.root, self.log_viewer)

        # メニューバーの構築
        self._setup_menubar()

    def _init_log_viewer(self) -> None:
        """ログウィンドウの初期化"""
        self.log_viewer_window = tk.Toplevel(self.root)
        self.log_viewer = LogViewer(self.log_viewer_window)
        self.log_viewer_window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _init_operation_panel(self) -> None:
        """操作パネルウィンドウの初期化"""
        self.operation_panel_window = tk.Toplevel(self.root)
        self.operation_panel = OperationPanel(self.operation_panel_window, self.sim_setting, self.log_viewer)
        self.operation_panel_window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_menubar(self) -> None:
        """メニューバーのセットアップ"""
        menu_builder = MenuBuilder(self.root)
        menu_builder.build_menu("Byte演算", self.byte_window_manager.create_window)
        menubar = menu_builder.get_menubar()

        # ウィンドウにメニューバーを設定
        self.operation_panel_window.config(menu=menubar)

    def on_closing(self) -> None:
        """アプリケーション終了時の処理"""
        if self.operation_panel.ble_client.scanning:
            self.operation_panel.stop_scan()
        self.operation_panel.loop.call_soon_threadsafe(self.operation_panel.loop.stop)

        # Byte演算ウィンドウをすべて閉じる
        self.byte_window_manager.close_all_windows()

        self.root.destroy()

    def run(self) -> None:
        """アプリケーション起動"""
        self.log_viewer.add_log("情報", "アプリケーションを起動しました。")
        self.root.mainloop()


def main() -> None:
    ble_manager = BLEManager()
    ble_manager.run()


if __name__ == "__main__":
    main()
