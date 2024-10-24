import asyncio
import io
import logging
from typing import Tuple

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError

import utility
from read_command import SimCommand
from read_send_list import CommandList
from read_setting import SimSetting

FILE_NAME_SETTING = r"./settings/setting.yaml"
FILE_NAME_COMMAND = r"./settings/command.yaml"
FILE_NAME_SEND_LIST = r"./settings/send_list.yaml"


async def scan_device(bd_addr_r: str) -> BLEDevice:
    """指定されたデバイスを検索する

    Args:
        bd_addr_r (str): 検索したいBDアドレスを指定

    Returns:
        BLEDevice: BLEDevice情報を返す
    """
    bd_adrs_list: list[str] = []

    async with BleakScanner() as scanner:
        print("Scanning...")

        n = 5
        print(f"\nFind device with name longer than {n} characters...")
        async for bd, ad in scanner.advertisement_data():
            # 検出済みのBDアドレスは無視
            if bd.address in bd_adrs_list:
                continue

            # 未検出のBDアドレスを処理する
            bd_adrs_list.append(bd.address)

            # 結果を出力する
            found = len(bd.name or "") > n or len(ad.local_name or "") > n
            print(f" Found{' it' if found else ''} {bd!r}")

            # デバイス名を含まない場合何もしない
            if found is not True:
                continue

            if bd_addr_r == bd.address:
                print(f"Found: {bd.name}, BDAddress:{bd.address}")
                break

    return bd


def show_client_info(client_r: BleakClient) -> None:
    """接続先から取得できる情報を表示する

    Args:
        client_r (BleakClient): 情報表示したい接続先
    """
    print(f"MTU size{client_r.mtu_size}")

    # サービスとCharacteristicを表示
    for service in client_r.services:
        print(f"Service: {service.uuid}")
        for char in service.characteristics:
            print(f"  Characteristic: {char.uuid}, Handle: {char.handle}")


def make_command(
    count_r: int,
    cmnd_r: SimCommand,
    tgt_cmnd_r: str,
    tgt_type_r: int,
) -> Tuple[bytearray, int, int]:
    write_value = bytearray()
    handle_wr = 0
    handle_nt = 0
    for write_data in cmnd_r.write_data_list:
        if tgt_cmnd_r != write_data.cmnd_name:
            continue

        for detail_data in write_data.detali_list:
            if tgt_type_r != detail_data.detail_type:
                continue

            send_data_list: list[int] = []
            send_data_list.extend(detail_data.detail_head)
            send_data_list.append(count_r)
            send_data_list.append(detail_data.detail_type)

            if tgt_type_r in cmnd_r.write_info.type_list:
                send_data_list.append(write_data.cmnd_type)
            else:
                send_data_list.append(write_data.cmnd_type_detail)
                send_data_list.append(detail_data.detail_mode)

            send_data_list.extend(detail_data.detail_body)

            check_sum = utility.get_check_sum(send_data_list)
            send_data_list.extend(check_sum)
            write_value = bytearray(send_data_list)

            handle_wr = write_data.handle_write
            handle_nt = write_data.handle_notify

    if len(write_value) == 0:
        raise ValueError(f"存在しないコマンドが指定されています。{tgt_cmnd_r=}, {handle_nt=}")

    return (write_value, handle_wr, handle_nt)


async def connect_device(device_r: BLEDevice) -> None:
    """指定されたBDアドレスのデバイスと接続する

    Args:
        device_r (BLEDevice): 接続したいBLEDevice
    """

    def handle_disconnect(_: BleakClient) -> None:
        """実行中のタスクを中断して終了する

        Args:
            _ (BleakClient): 読み捨て
        """
        print("Device was disconnected, goodbye.")
        for task in asyncio.all_tasks():
            task.cancel()

    def handle_notification(_: BleakGATTCharacteristic, data: bytearray) -> None:
        """ペリフェラルのnotifyを表示する

        Args:
            _ (BleakGATTCharacteristic): 読み捨て
            data (bytearray): notifyの受信値
        """
        print(f"notify: {data}")

    print("Connecting...")
    async with BleakClient(
        device_r,
        disconnected_callback=handle_disconnect,
        winrt={"use_cached_services": True},
    ) as client:
        print("Connected")
        # show_client_info(client)
        cmnd = SimCommand(FILE_NAME_COMMAND)

        for rd in cmnd.read_data_list:
            rd.rcv_data = await client.read_gatt_char(rd.handle, use_cached=True)
            print(f'  {rd.name}: {"".join(map(chr, rd.rcv_data))}')

        command_list = CommandList(FILE_NAME_SEND_LIST)
        get_cmnd = command_list.get_command_dict("first")
        if get_cmnd is not None:
            count = 0
            for send_list in get_cmnd[CommandList.KEY_SEND_LIST]:
                write_value, hndl_wr, hndl_nt = make_command(count, cmnd, send_list[0], send_list[1])
                await client.write_gatt_char(hndl_wr, write_value, response=False)
                await client.start_notify(hndl_nt, handle_notification)
                count = count + 1

        print("Diconnect...")
        await client.disconnect()


async def main() -> bool:
    """Bleakメイン処理

    Returns:
        bool: True: 再度実行する, False: 終了する
    """
    sim_setting = SimSetting(FILE_NAME_SETTING)
    bd_adrs = sim_setting.get_bd_adrs()[0]
    if bd_adrs is None:
        return False

    # 接続対象のスキャン
    device = await scan_device(bd_adrs)
    # 対象と接続
    try:
        await connect_device(device)
    except asyncio.exceptions.CancelledError:
        logging.warning("タスク中断")
        return False
    except asyncio.exceptions.TimeoutError:
        logging.warning("タスクタイムアウト")
        return True
    except BleakError as e:
        logging.warning(f"BleakError: {e}")
        return True

    return False


# ログ用のstream用意
log_stream = io.StringIO()

# ログの設定
logging.basicConfig(
    stream=log_stream,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


if __name__ == "__main__":
    retry = True
    while retry is True:
        retry = asyncio.run(main())


# ログ出力
print(log_stream.getvalue())
