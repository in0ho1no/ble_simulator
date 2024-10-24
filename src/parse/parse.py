import io
import logging

import parse_PacketData

SRC_FILE_PATH = r"other_in\20240716_2_pc2fpb_2a24-2a00.psd"
DST_FILE_PATH = r"other_out\output.csv"


def main() -> None:
    # 対象ファイルを読み込む
    with open(SRC_FILE_PATH, "rb") as f:
        file_contents = f.read()

    # バイナリデータをパケットデータとして取得
    packet_list = parse_PacketData.get_packet_list(file_contents)
    logging.info(f"Packet Count {len(packet_list)}")

    # 結果出力
    with open(DST_FILE_PATH, "w") as f:
        for packet in packet_list:
            result = f"\
    {packet.fld_no_m.get_data()},\
    {packet.timestamp_m},\
    {packet.fld_status_bytes_m.channel_m},\
    {hex(packet.fld_payload_m.access_adrs_m)},\
    {packet.fld_status_bytes_m.rssi_m},\
    {packet.fld_status_bytes_m.indicate_crc_m},\
    {packet.fld_payload_m.get_ble_payload_hex()},\
    \r\n"
            f.write(result)


# ログ用のstream用意
log_stream = io.StringIO()

# ログの設定
logging.basicConfig(
    stream=log_stream,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    main()

# ログ出力
print(log_stream.getvalue())
