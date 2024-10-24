"""PSDファイルに格納されたパケットのうち Status bytes を扱う"""


class StatusBytes:
    """Status bytesの情報"""

    def __init__(self, raw_data_r: bytes) -> None:
        self.raw_data_m = raw_data_r

        self.__set_rssi()
        self.__set_indicate_crc()
        self.__set_channel()

    def __set_rssi(self) -> None:
        """RSSIを保持する"""
        # デバイスに応じたオフセットを加味した値を保持する
        self.rssi_m = -94 + self.raw_data_m[0]

    def __set_indicate_crc(self) -> None:
        """CRCの状態を保持する
        True: OK、False: NG
        """
        if (self.raw_data_m[1] & 0x80) >> 7:
            self.indicate_crc_m = True
        else:
            self.indicate_crc_m = False

    def __set_channel(self) -> None:
        """channelを保持する"""
        self.channel_m = self.raw_data_m[1] & 0x7F
