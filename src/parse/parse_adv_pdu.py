"""アドバタイジングパケットの解析を行う"""

import logging

PDU_TYPE_IND = 0
PDU_TYPE_DIRECT_IND = 1
PDU_TYPE_NONCONN_IND = 2
PDU_TYPE_SCAN_REQ = 3
PDU_TYPE_SCAN_RSP = 4
PDU_TYPE_CONNECT_IND = 5
PDU_TYPE_SCAN_IND = 6


class AdvertisePdu:
    def __init__(self, raw_data_r: bytes) -> None:
        self.data_m = raw_data_r

        self.__set_pdu_type()

    def __set_pdu_type(self) -> None:
        """アドバタイジングパケットを分類する"""
        value = self.data_m[0] & 0x0F
        if value == 0:
            self.self_pdu_type_m = PDU_TYPE_IND
        elif value == 1:
            self.self_pdu_type_m = PDU_TYPE_DIRECT_IND
        elif value == 2:
            self.self_pdu_type_m = PDU_TYPE_NONCONN_IND
        elif value == 3:
            self.self_pdu_type_m = PDU_TYPE_SCAN_REQ
        elif value == 4:
            self.self_pdu_type_m = PDU_TYPE_SCAN_RSP
        elif value == 5:
            self.self_pdu_type_m = PDU_TYPE_CONNECT_IND
        elif value == 6:
            self.self_pdu_type_m = PDU_TYPE_SCAN_IND
        else:
            logging.warn(f"Err PDU Type {value}")
            self.self_pdu_type_m = 0xFF
