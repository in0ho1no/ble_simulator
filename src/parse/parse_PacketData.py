import logging

from parse_adv_pdu import AdvertisePdu
from parse_PSD_head import FieldInformation as FInfo
from parse_PSD_head import FieldLength as FLength
from parse_PSD_head import FieldNumber as FNumber
from parse_PSD_head import FieldPayloadWStatusbytes as FPayloadWSb
from parse_PSD_head import FieldTimestamp as FTimeStamp
from parse_PSD_Payload import Payload
from parse_PSD_SB import StatusBytes

ADVERTISING_PACKET_ACCESS_ADRS = 0x8E89BED6
ADVERTISING_PACKET_CHANNEL_LIST = [37, 38, 39]


class PacketData:
    def __init__(self, info_r: FInfo, no_r: FNumber, time_r: FTimeStamp, len_r: FLength, pay_r: FPayloadWSb) -> None:
        self.fld_info_m = info_r
        self.fld_no_m = no_r
        self.fld_timestamp_m = time_r
        self.fld_length_m = len_r
        self.fld_payload_w_sb_m = pay_r

        self.__set_payload()
        self.__set_status_bytes()

        self.__set_pdu_type()

    def __set_payload(self) -> None:
        """payloadをbytesデータのまま保持する"""
        raw_data = self.fld_payload_w_sb_m.data_m[: self.fld_length_m.get_data() - 2]
        self.fld_payload_m = Payload(raw_data)

    def __set_status_bytes(self) -> None:
        """status bytesをbytesデータのまま保持する"""
        raw_data = self.fld_payload_w_sb_m.data_m[self.fld_length_m.get_data() - 2 : self.fld_length_m.get_data()]
        self.fld_status_bytes_m = StatusBytes(raw_data)

    def set_timestamp(self, time_us: int) -> None:
        """0起算のタイムスタンプを保持する

        Args:
            time_us (int): 最初の受信したデータを基準点(0)としたタイムスタンプ
        """
        self.timestamp_m = time_us

    def __set_pdu_type(self) -> None:
        # CRCがエラーの場合、解析しても意味がないので何もせずに終了する
        if self.fld_status_bytes_m.indicate_crc_m is False:
            return

        if ADVERTISING_PACKET_ACCESS_ADRS == self.fld_payload_m.access_adrs_m:
            if self.fld_status_bytes_m.channel_m in ADVERTISING_PACKET_CHANNEL_LIST:
                # Access Address と Channelの両方を満足したとき Advertise Packet とみなす
                AdvertisePdu(self.fld_payload_m.ble_header)
            else:
                # Channelが異なるので読み捨てる
                logging.warn("Err")
        else:
            if self.fld_status_bytes_m.channel_m in ADVERTISING_PACKET_CHANNEL_LIST:
                # Channelが異なるので読み捨てる
                logging.warn("Err")
            else:
                # Access Address と Channelの両方を満足したとき DataPhys Packet とみなす
                # logging.debug(f"Phy: {self.fld_payload_m.access_adrs_m}, {self.fld_status_bytes_m.channel_m}")
                pass


def get_packet_list(file_contents_r: bytes) -> list[PacketData]:
    # パケット数を計算しておく
    packet_size = FInfo.length_m + FNumber.length_m + FTimeStamp.length_m + FLength.length_m + FPayloadWSb.length_m
    total_packet = int(len(file_contents_r) / packet_size)

    cnt = 0
    psd_list: list[PacketData] = []
    while file_contents_r:
        print(f"\rGetting... {cnt:0{len(str(total_packet))}}:{total_packet}", end="")

        # フィールド単位で格納する
        pkt_info = FInfo()
        pkt_no = FNumber()
        pkt_time = FTimeStamp()
        pkt_len = FLength()
        pkt_payload = FPayloadWSb()

        file_contents_r = pkt_info.hold_data(file_contents_r)
        file_contents_r = pkt_no.hold_data(file_contents_r)
        file_contents_r = pkt_time.hold_data(file_contents_r)
        file_contents_r = pkt_len.hold_data(file_contents_r)
        file_contents_r = pkt_payload.hold_data(file_contents_r)
        pkt = PacketData(pkt_info, pkt_no, pkt_time, pkt_len, pkt_payload)

        # タイムスタンプを0リセットする
        if 0 == cnt:
            base_time_us = pkt_time.get_data()
        pkt.set_timestamp(pkt_time.get_data() - base_time_us)

        psd_list.append(pkt)
        cnt += 1

    print(f"\rCompleted! {cnt}:{total_packet}")
    return psd_list
