"""PSDファイルに格納されたパケットのうち Payload を扱う"""


class Payload:
    """payload の情報"""

    def __init__(self, raw_data_r: bytes) -> None:
        self.raw_data_m = raw_data_r

        self.__set_length()
        self.__set_access_adrs()
        self.__set_ble_header()
        self.__set_ble_payload()
        self.__set_crc()

    def __set_length(self) -> None:
        """BLE Devices の Length を保持する"""
        self.length_m = self.raw_data_m[0 : 0 + 1].hex()

    def __set_access_adrs(self) -> None:
        """BLE Devices の Access Address を保持する"""
        adrs_bytes = self.raw_data_m[1 : 1 + 4]
        self.access_adrs_m = int.from_bytes(adrs_bytes, "little")

    def __set_ble_header(self) -> None:
        """BLE Devices の BLE Header を保持する"""
        self.ble_header = self.raw_data_m[5 : 5 + 2]

    def __set_ble_payload(self) -> None:
        """BLE Devices の Payload を保持する"""
        self.ble_payload = self.raw_data_m[7:-3]

    def __set_crc(self) -> None:
        """BLE Devices の CRC を保持する"""
        crc_bytes = self.raw_data_m[-3:]
        self.crc_m = hex(int.from_bytes(crc_bytes, "little")).upper()

    def get_ble_payload_hex(self) -> str:
        """payload情報を16進文字列で取得する

        Returns:
            str: カンマで区切られた16進文字列のpayload情報
        """
        return ",".join([f"{byte:02x}" for byte in self.ble_payload])
