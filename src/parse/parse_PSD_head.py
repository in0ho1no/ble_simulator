"""PSDファイルに格納されたパケットのうちヘッダ部分を扱う"""


class FieldCommon:
    """パケット内に共通するフィールドの情報"""

    length_m: int
    mean_m: str

    def __init__(self, length_r: int, meaning_r: str) -> None:
        self.length_m = length_r
        self.mean_m = meaning_r
        self.data_m: bytes = b""

    def hold_data(self, bytes_data_r: bytes) -> bytes:
        """bytesデータからフィールドに応じたデータを保持する

        Args:
            bytes_data_r (bytes): データを取得したいbytesデータ

        Returns:
            bytes: 引数で与えられたbytesデータのうち保持しなかった分のデータ
        """
        self.data_m = bytes_data_r[: self.length_m]
        return bytes_data_r[self.length_m :]


class FieldInformation(FieldCommon):
    """Packet Information フィールド固有の情報"""

    length_m = 1
    mean_m = "Packet_Information"

    def __init__(self) -> None:
        super().__init__(self.length_m, self.mean_m)


class FieldNumber(FieldCommon):
    """Packet Number フィールド固有の情報"""

    length_m = 4
    mean_m = "Packet_Number"

    def __init__(self) -> None:
        super().__init__(self.length_m, self.mean_m)

    def get_data(self) -> int:
        """パケット番号を取得する

        Returns:
            int: パケット番号
        """
        return int.from_bytes(self.data_m, "little")


class FieldTimestamp(FieldCommon):
    """Timestamp フィールド固有の情報"""

    length_m = 8
    mean_m = "Timestamp_ms"

    def __init__(self) -> None:
        super().__init__(self.length_m, self.mean_m)

    def get_data(self) -> int:
        """タイムスタンプを取得する

        0起算ではないので注意
        Returns:
            int: 取得したタイムスタンプ[us]
        """
        time_ms = int.from_bytes(self.data_m, "little")
        time_lo = time_ms & 0xFFFF
        time_hi = time_ms >> 16
        time_stamp = time_hi * 5000 + time_lo
        time_stamp_us = time_stamp / 32
        return int(time_stamp_us)


class FieldLength(FieldCommon):
    """Length フィールド固有の情報"""

    length_m = 2
    mean_m = "PacketLength"

    def __init__(self) -> None:
        super().__init__(self.length_m, self.mean_m)

    def get_data(self) -> int:
        """Payload+StatusBytes長を取得する

        Returns:
            int: Payload+StatusBytes長
        """
        return int.from_bytes(self.data_m, "little")


class FieldPayloadWStatusbytes(FieldCommon):
    """Payload フィールド固有の情報"""

    length_m = 256
    mean_m = "PayloadData"

    def __init__(self) -> None:
        super().__init__(self.length_m, self.mean_m)
