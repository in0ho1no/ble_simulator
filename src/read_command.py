from typing import Any

import yaml  # type: ignore


class ReadData:
    KEY_FUNC = "func"
    KEY_FUNC_NAME = "name"
    KEY_FUNC_HANDLE = "handle"

    func: str
    name: str
    handle: int
    rcv_data: Any

    def __init__(self, read_data_r: dict) -> None:
        self.func = read_data_r[self.KEY_FUNC]
        self.name = read_data_r[self.KEY_FUNC_NAME]
        self.handle = read_data_r[self.KEY_FUNC_HANDLE]
        self.rcv_data = ""


class WriteInfo:
    KEY_TYPE_LIST = "type_list"

    type_list: list[int]

    def __init__(self, data_r: dict) -> None:
        self.type_list = data_r[self.KEY_TYPE_LIST]


class DetailData:
    KEY_DETAIL_TYPE = "type"
    KEY_DETAIL_HEAD = "head"
    KEY_DETAIL_MODE = "mode"
    KEY_DETAIL_BODY = "body"

    detail_type: int
    detail_head: list[int]
    detail_mode: int
    detail_body: list[int]

    def __init__(self, detail_data_r: dict) -> None:
        self.detail_type = detail_data_r[self.KEY_DETAIL_TYPE]
        self.detail_head = detail_data_r[self.KEY_DETAIL_HEAD]
        self.detail_mode = detail_data_r[self.KEY_DETAIL_MODE]
        self.detail_body = detail_data_r[self.KEY_DETAIL_BODY]


class WriteData:
    KEY_CMND_NAME = "cmnd_name"
    KEY_CMND_TYPE = "cmnd_type"
    KEY_CMND_TYPE_DETAIL = "cmnd_type_detail"
    KEY_HNDL_WRITE = "handle_write"
    KEY_HNDL_NOTIFY = "handle_notify"

    KEY_DETAIL = "detail"

    cmnd_name: str
    cmnd_type: int
    cmnd_detail: int
    handle_write: int
    handle_notify: int
    detali_list: list[DetailData]

    def __init__(self, write_data_r: dict) -> None:
        self.cmnd_name = write_data_r[self.KEY_CMND_NAME]
        self.cmnd_type = write_data_r[self.KEY_CMND_TYPE]
        self.cmnd_type_detail = write_data_r[self.KEY_CMND_TYPE_DETAIL]
        self.handle_write = write_data_r[self.KEY_HNDL_WRITE]
        self.handle_notify = write_data_r[self.KEY_HNDL_NOTIFY]
        self.detali_list = []
        for detail in write_data_r[self.KEY_DETAIL]:
            self.detali_list.append(DetailData(detail))


class SimCommand:
    """設定ファイルから読み込んだ情報を保持する"""

    KEY_RW_R = "read"
    KEY_WRITE_INFO = "write_info"
    KEY_RW_W = "write"

    read_data_list: list[ReadData]
    write_info: WriteInfo
    write_data_list: list[WriteData]

    def __init__(self, filepath_r: str) -> None:
        """設定ファイルを読み込む"""
        self.filepath_m = filepath_r
        with open(self.filepath_m, encoding="utf-8") as f:
            try:
                data_rd = yaml.safe_load(f)

                self.read_data_list = []
                for inner in data_rd[self.KEY_RW_R]:
                    self.read_data_list.append(ReadData(inner))

                self.write_info = WriteInfo(data_rd[self.KEY_WRITE_INFO])

                self.write_data_list = []
                for inner in data_rd[self.KEY_RW_W]:
                    self.write_data_list.append(WriteData(inner))

            except yaml.YAMLError as e:
                print(f"YAMLファイルの解析中にエラーが発生しました: {e}")
                return None


if __name__ == "__main__":
    FILE_NAME_COMMAND = r"./src/settings/command.yaml"
    cmnd = SimCommand(FILE_NAME_COMMAND)
    for read_data in cmnd.read_data_list:
        print(read_data)

    print(cmnd.write_info.type_list)

    for write_data in cmnd.write_data_list:
        print(write_data)
