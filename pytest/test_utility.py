import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..//src"))


import utility  # type: ignore


@pytest.mark.parametrize(
    "int_data_list, expected_result",
    [
        ([], 0),
        ([0x05], 0x05),
        ([0x01, 0x02, 0x03, 0x04, 0x05], 0x0F),
        ([-1, -2, 3, 4, -5], -1),
        ([1000000, 2000000, 3000000], 6000000),
    ],
)
def test_calc_check_sum(int_data_list: list[int], expected_result: int) -> None:
    assert utility.calc_check_sum(int_data_list) == expected_result


@pytest.mark.parametrize(
    "target_value, expected_result",
    [
        (0, [0, 0]),
        (359, [0x01, 0x67]),
        (65535, [0xFF, 0xFF]),
    ],
)
def test_convert_int2two_byte_list(target_value: int, expected_result: list[int]) -> None:
    assert utility.convert_int2two_byte_list(target_value) == expected_result


@pytest.mark.parametrize(
    "int_data_list, expected_result",
    [
        ([], [0x00, 0x00]),
        ([0x05], [0x05, 0x00]),
        ([0x01, 0x02, 0x03, 0x04, 0x05], [0x0F, 0x00]),
        ([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF], [0xFB, 0x04]),
    ],
)
def test_get_check_sumt(int_data_list: list[int], expected_result: list[int]) -> None:
    assert utility.get_check_sum(int_data_list) == expected_result


# pytestを使ったテストの実行
if __name__ == "__main__":
    pytest.main()
