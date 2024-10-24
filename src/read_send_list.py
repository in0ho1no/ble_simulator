import yaml  # type: ignore


class CommandList:
    """ファイルから読み込んだ情報を保持する"""

    KEY_COMMAND_LIST = "command_list"
    KEY_COMMAND = "command"
    KEY_SEND_LIST = "send_list"

    cmnd_list: list[dict]

    def __init__(self, filepath_r: str) -> None:
        """ファイルを読み込む"""
        self.filepath_m = filepath_r
        with open(self.filepath_m, encoding="utf-8") as f:
            try:
                data_rd = yaml.safe_load(f)
                self.cmnd_list = data_rd[self.KEY_COMMAND_LIST]

            except yaml.YAMLError as e:
                print(f"YAMLファイルの解析中にエラーが発生しました: {e}")
                return None

    def get_command_dict(self, tgt_cmnd_r: str) -> None | dict:
        """指定されたコマンドに対応するディクショナリをリストから取得する

        Args:
            command_list_r (list[dict]): コマンドディクショナリのリスト
            tgt_cmnd_r (str): 取得したいコマンド名

        Returns:
            None | dict: 指定されたコマンドに対応するディクショナリ、見つからない場合はNone
        """
        try:
            return next(item for item in self.cmnd_list if item[self.KEY_COMMAND] == tgt_cmnd_r)
        except StopIteration:
            return None


if __name__ == "__main__":
    FILE_NAME_SEND_LIST = r"./src/settings/send_list.yaml"
    cmnd = CommandList(FILE_NAME_SEND_LIST)
    # print(cmnd.cmnd_list)
    get_cmnd = cmnd.get_command_dict("first")
    if get_cmnd is not None:
        print(get_cmnd)
        for data in get_cmnd[cmnd.KEY_SEND_LIST]:
            print(data[0], data[1])
