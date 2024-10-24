def calc_check_sum(data_list_r: list[int]) -> int:
    """与えられたint型リストの総和を返す

    Args:
        data_list_r (list[int]): チェックサムを求めたいリスト

    Returns:
        int: 総和
    """
    sum = 0

    for data in data_list_r:
        sum = sum + data

    return sum


def convert_int2two_byte_list(tgt_r: int) -> list[int]:
    """10進整数を2バイトのint型リストに変換する

    Args:
        tgt_r (int): 変換する10進整数（0-65535の範囲）

    Raises:
        ValueError: 入力値が0-65535の範囲外の場合

    Returns:
        list[int]: 2バイトのint型リスト
    """
    # 例外処理
    if not 0 <= tgt_r <= 65535:
        raise ValueError("入力値は0から65535の範囲内である必要があります")

    # 上位バイト（8-15ビット）を取得
    high_byte = (tgt_r >> 8) & 0xFF

    # 下位バイト（0-7ビット）を取得
    low_byte = tgt_r & 0xFF

    return [high_byte, low_byte]


def get_check_sum(data_list_r: list[int]) -> list[int]:
    """チェックサムの配列を取得する

    Args:
        data_list_r (list[int]): チェックサムを取得したいリスト

    Returns:
        list[int]: 2byteのチェックサムを上下入れ替えて返す
    """
    sum = calc_check_sum(data_list_r)
    two_byte_list = convert_int2two_byte_list(sum)
    return [two_byte_list[1], two_byte_list[0]]
