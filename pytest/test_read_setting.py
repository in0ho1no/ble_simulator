import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import mock_open, patch

import yaml  # type: ignore

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "..//src"))


from read_setting import SimSetting, is_hex  # type: ignore

FILE_NAME_SETTING = r"./src/settings/setting.yaml"


@pytest.fixture
def sim_setting(tmp_path: Path) -> SimSetting:
    yaml_file = tmp_path / "test_config.yaml"
    yaml_file.write_text(yaml.dump({"info": {"bdaddress": ["aa:bb:cc:dd:ee:ff"]}}))
    return SimSetting(str(yaml_file))


# add_bd_adrsのテストケース
@pytest.mark.parametrize(
    "new_bd_address, expected_result, expected_list",
    [
        ("11:22:33:44:55:66", True, ["aa:bb:cc:dd:ee:ff", "11:22:33:44:55:66"]),  # 正しい形式、追加成功
        ("aa:bb:cc:dd:ee:ff", False, ["aa:bb:cc:dd:ee:ff"]),  # 既存のアドレス、追加失敗
        ("GG:HH:II:JJ:KK:LL", False, ["aa:bb:cc:dd:ee:ff"]),  # 無効なアドレス、追加失敗
    ],
)
def test_add_bd_adrs(sim_setting: SimSetting, new_bd_address: str, expected_result: bool, expected_list: list) -> None:
    result = sim_setting.add_bd_adrs(new_bd_address)
    assert result == expected_result
    assert sim_setting.get_bd_adrs() == expected_list

    # YAMLファイルが正しく更新されたことを確認
    with open(sim_setting.filepath_m) as f:
        saved_data = yaml.safe_load(f)
        assert saved_data["info"]["bdaddress"] == expected_list


# remove_bd_adrsのテストケース
@pytest.mark.parametrize(
    "remove_bd_address, expected_result, expected_list",
    [
        ("aa:bb:cc:dd:ee:ff", True, []),  # 存在するアドレス、削除成功
        ("11:22:33:44:55:66", False, ["aa:bb:cc:dd:ee:ff"]),  # 存在しないアドレス、削除失敗
        ("GG:HH:II:JJ:KK:LL", False, ["aa:bb:cc:dd:ee:ff"]),  # 無効なアドレス、削除失敗
    ],
)
def test_remove_bd_adrs(sim_setting: SimSetting, remove_bd_address: str, expected_result: bool, expected_list: list[str]) -> None:
    result = sim_setting.remove_bd_adrs(remove_bd_address)
    assert result == expected_result
    assert sim_setting.get_bd_adrs() == expected_list

    # YAMLファイルが正しく更新されたことを確認
    with open(sim_setting.filepath_m) as f:
        saved_data = yaml.safe_load(f)
        assert saved_data["info"]["bdaddress"] == expected_list


# 複数の操作を組み合わせたテストケース
def test_multiple_operations(sim_setting: SimSetting) -> None:
    # 初期状態を確認
    assert sim_setting.get_bd_adrs() == ["aa:bb:cc:dd:ee:ff"]

    # 新しいアドレスを追加
    assert sim_setting.add_bd_adrs("11:22:33:44:55:66") is True
    assert sim_setting.get_bd_adrs() == ["aa:bb:cc:dd:ee:ff", "11:22:33:44:55:66"]

    # 既存のアドレスを削除
    assert sim_setting.remove_bd_adrs("aa:bb:cc:dd:ee:ff") is True
    assert sim_setting.get_bd_adrs() == ["11:22:33:44:55:66"]

    # 存在しないアドレスの削除を試みる
    assert sim_setting.remove_bd_adrs("aa:bb:cc:dd:ee:ff") is False
    assert sim_setting.get_bd_adrs() == ["11:22:33:44:55:66"]

    # 無効なアドレスの追加を試みる
    assert sim_setting.add_bd_adrs("invalid_address") is False
    assert sim_setting.get_bd_adrs() == ["11:22:33:44:55:66"]

    # YAMLファイルが正しく更新されたことを確認
    with open(sim_setting.filepath_m) as f:
        saved_data = yaml.safe_load(f)
        assert saved_data["info"]["bdaddress"] == ["11:22:33:44:55:66"]


# Trueを期待するテストケース
@pytest.mark.parametrize(
    "input_str",
    [
        "1a2b3c",  # 小文字の16進数
        "ABCDEF",  # 大文字の16進数
        "1234567890",  # 数字のみ
        "aBcD1234",  # 大文字小文字混在
        "abcdef",  # 小文字のみ
        "ABC123",  # 大文字と数字
        "0",  # 単一の数字
        "f",  # 単一の小文字
        "F",  # 単一の大文字
    ],
)
def test_is_hex_true(input_str: str) -> None:
    assert is_hex(input_str) is True


# Falseを期待するテストケース
@pytest.mark.parametrize(
    "input_str",
    [
        "1g2h3i",  # 16進数ではない文字を含む
        "XYZ",  # 16進数に含まれないアルファベット
        "123g456",  # 'g' は16進数ではない
        "123 456",  # スペースが含まれる
        "12-34",  # ハイフンが含まれる
        "12.34",  # ドットが含まれる
        "GHIJKL",  # 大文字の16進数に含まれない文字
        "",  # 空文字
        "!@#$%^",  # 特殊記号
        "12\n34",  # 改行が含まれる
        "12\t34",  # タブが含まれる
    ],
)
def test_is_hex_false(input_str: str) -> None:
    assert is_hex(input_str) is False


# BDアドレスが有効な場合のテストケース
@pytest.mark.parametrize(
    "bd_address, expected_result",
    [
        ("01:23:45:67:89:AB", ["01:23:45:67:89:AB"]),  # 正しい形式
        ("11:22:33:44:55:66", ["11:22:33:44:55:66"]),  # 正しい形式
        ("AA:BB:CC:DD:EE:FF", ["AA:BB:CC:DD:EE:FF"]),  # 正しい形式
    ],
)
def test_valid_bd_adrs(sim_setting: SimSetting, bd_address: str, expected_result: str) -> None:
    # read_setting を実行
    mock_yaml_data = yaml.dump({"info": {"bdaddress": [bd_address]}})
    with patch("builtins.open", mock_open(read_data=mock_yaml_data)):
        sim_setting.read_setting()

    # BDアドレスが空文字であることを確認
    assert sim_setting.get_bd_adrs() == expected_result


# BDアドレスが無効な場合のテストケース
@pytest.mark.parametrize(
    "invalid_bd_address",
    [
        "01:23:45:67:89",  # 不足している
        "01-23-45-67-89",  # 区切り文字が異なる
        "01 23 45 67 89",  # 区切り文字が異なる
        "01:23:45:67:89:GH",  # 16進数でない文字が含まれる
        "0123456789AB",  # コロンで区切られていない
        "01:23:45:67:89:ABC",  # 区切られている文字列が2文字以上の部分がある
        "01:23:45:67:89:AB:CD",  # 余分な部分がある
    ],
)
def test_invalid_bd_adrs(sim_setting: SimSetting, invalid_bd_address: str) -> None:
    # read_setting を実行
    mock_yaml_data = yaml.dump({"info": {"bdaddress": invalid_bd_address}})
    with patch("builtins.open", mock_open(read_data=mock_yaml_data)):
        sim_setting.read_setting()

    # BDアドレスが空文字であることを確認
    assert sim_setting.get_bd_adrs() == []


# pytestを使ったテストの実行
if __name__ == "__main__":
    pytest.main()
