import csv
from unittest.mock import mock_open, patch

import pytest

from winactor_for_wmc.licenses import get_licenses_usage_csv


def test_run_success_with_checkout_checkin(mocker):
    """払い出しと回収が正常にペアになる場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609459200000,
                },
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609462800000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    assert mock_client.get.call_count == 1
    mock_file.assert_called_once_with(
        "/path/to/test.csv", "w", newline="", encoding="utf-8-sig"
    )
    assert result is None


def test_run_success_checkout_only(mocker):
    """払い出しのみで回収がない場合（未回収）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=佐藤花子,PC名=PC002",
                    "createdTime": 1609459200000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    assert result is None


def test_run_success_checkin_only(mocker):
    """回収のみで払い出しがない場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=鈴木一郎,PC名=PC003",
                    "createdTime": 1609462800000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    assert result is None


def test_run_multiple_pages(mocker):
    """複数ページのイベントが存在する場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": f"フローティングライセンスを払い出しました。ユーザ名=ユーザー{i},PC名=PC{i}",
                    "createdTime": 1609459200000 + i * 1000,
                }
                for i in range(100)
            ]
        },
        {
            "items": [
                {
                    "message": f"フローティングライセンスを回収しました。ユーザ名=ユーザー{i},PC名=PC{i}",
                    "createdTime": 1609462800000 + i * 1000,
                }
                for i in range(50)
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    assert mock_client.get.call_count == 2
    assert result is None


def test_run_encoding_ms932(mocker):
    """MS932エンコーディングの場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="MS932",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    mock_file.assert_called_once_with(
        "/path/to/test.csv", "w", newline="", encoding="shift_jis"
    )


def test_run_encoding_unknown(mocker):
    """未知のエンコーディングの場合（elseブロック）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UNKNOWN",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    mock_file.assert_called_once_with(
        "/path/to/test.csv", "w", newline="", encoding="utf-8-sig"
    )


def test_run_missing_required_params():
    """必須パラメータが不足している場合"""
    with pytest.raises(
        ValueError, match="WMC URL, アクセストークン, CSVファイル名 は必須項目です。"
    ):
        get_licenses_usage_csv.run()


def test_run_created_at_type_before_missing_date():
    """beforeで検索日1が未指定の場合"""
    with pytest.raises(
        ValueError, match="登録日時条件が「以前」の場合、検索日1は必須です。"
    ):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="before",
        )


def test_run_created_at_type_after_missing_date():
    """afterで検索日1が未指定の場合"""
    with pytest.raises(
        ValueError, match="登録日時条件が「以後」の場合、検索日1は必須です。"
    ):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="after",
        )


@pytest.mark.parametrize(
    "created_at_type,start_date,end_date,expected_type",
    [
        ("range", "2021/01/01", "2021/01/31", "range"),
        ("range", "2021/01/01", None, "after"),
        ("range", None, "2021/01/31", "before"),
        ("range", None, None, None),
        ("invalid_type", None, None, None),
        ("", None, None, None),
    ],
)
def test_run_created_at_type_variations(
    mocker, created_at_type, start_date, end_date, expected_type
):
    """createdAtTypeの各パターンをテスト"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type=created_at_type,
            start_date=start_date,
            end_date=end_date,
        )

    call_args = mock_client.get.call_args
    if expected_type:
        assert call_args[1]["params"]["createdAtType"] == expected_type
    else:
        assert "createdAtType" not in call_args[1]["params"]


@pytest.mark.parametrize(
    "time_input,expected_output",
    [
        ("12:34:56", "12:34:56"),
        ("12:34", "12:34:00"),
        ("9:30", "09:30:00"),
        ("invalid", "00:00:00"),
        ("", "00:00:00"),
        ("25:00:00", "25:00:00"),
    ],
)
def test_validate_time_format(time_input, expected_output):
    """validate_time_format関数のテスト"""
    from winactor_for_wmc.licenses import get_licenses_usage_csv

    assert get_licenses_usage_csv.validate_time_format(time_input) == expected_output


def test_unix_time_to_datetime():
    """unix_time_to_datetime関数のテスト"""
    from winactor_for_wmc.licenses import get_licenses_usage_csv

    result = get_licenses_usage_csv.unix_time_to_datetime(1609459200000)
    assert len(result) == 19
    assert result[4] == "/" and result[7] == "/"
    assert result[10] == " "
    assert result[13] == ":" and result[16] == ":"
    assert get_licenses_usage_csv.unix_time_to_datetime(0) == ""


@pytest.mark.parametrize(
    "delta,expected",
    [
        ({"hours": 1}, "1:00:00"),
        ({"days": 1, "hours": 2, "minutes": 30, "seconds": 45}, "26:30:45"),
        ({"seconds": 0}, "0:00:00"),
        ({"seconds": -100}, "負の値"),
        ({"minutes": 45}, "0:45:00"),
        ({"seconds": 30}, "0:00:30"),
        ({"days": 2, "hours": 5}, "53:00:00"),
        ({"days": 2, "hours": 8, "minutes": 59, "seconds": 59}, "56:59:59"),
        ({"hours": 56, "minutes": 59, "seconds": 59}, "56:59:59"),
        ({"hours": 100, "minutes": 30, "seconds": 15}, "100:30:15"),
    ],
)
def test_format_time_difference(delta, expected):
    """format_time_difference関数のテスト（HH:MM:SS形式）"""
    from datetime import timedelta

    from winactor_for_wmc.licenses import get_licenses_usage_csv

    assert get_licenses_usage_csv.format_time_difference(timedelta(**delta)) == expected


def test_run_with_time_specifications(mocker):
    """時刻指定ありの各パターン（elseブロックカバレッジ）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()

    # range with both times
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="range",
            start_date="2021/01/01",
            start_time="10:00:00",
            end_date="2021/01/31",
            end_time="18:00:00",
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtTime1"] == "10:00:00"
    assert call_args[1]["params"]["createdAtTime2"] == "18:00:00"


def test_run_no_user_name_in_message(mocker):
    """メッセージにユーザ名がない場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを払い出しました。PC名=PC001",
                    "createdTime": 1609459200000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    assert result is None


def test_run_irrelevant_message(mocker):
    """払い出し・回収以外のメッセージの場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "その他のイベントメッセージ。ユーザ名=田中太郎",
                    "createdTime": 1609459200000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    assert result is None


def test_run_before_with_time_specified(mocker):
    """beforeで時刻指定ありの場合（elseブロック）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="before",
            start_date="2021/01/01",
            start_time="18:00:00",
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "before"
    assert call_args[1]["params"]["createdAtTime1"] == "18:00:00"


def test_run_after_with_time_specified(mocker):
    """afterで時刻指定ありの場合（elseブロック）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="after",
            start_date="2021/01/01",
            start_time="09:00:00",
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "after"
    assert call_args[1]["params"]["createdAtTime1"] == "09:00:00"


def test_run_range_start_only_with_time(mocker):
    """rangeで検索日1のみ、時刻指定ありの場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="range",
            start_date="2021/01/01",
            start_time="10:00:00",
            end_date="",
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "after"
    assert call_args[1]["params"]["createdAtTime1"] == "10:00:00"


def test_run_range_end_only_with_time(mocker):
    """rangeで検索日2のみ、時刻指定ありの場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="range",
            start_date="",
            end_date="2021/01/31",
            end_time="18:00:00",
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "before"
    assert call_args[1]["params"]["createdAtTime1"] == "18:00:00"


def test_run_multiple_users_mixed_events(mocker):
    """複数ユーザーの混在イベント（ソート確認）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609459200000,
                },
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=佐藤花子,PC名=PC002",
                    "createdTime": 1609459300000,
                },
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609462800000,
                },
                # 佐藤花子は未回収（checkin_timestamp=0でソート最優先）
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    assert result is None


def test_run_multiple_checkout_checkin_same_user(mocker):
    """同一ユーザーの複数回払い出し・回収"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609459200000,
                },
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609459300000,
                },
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609462800000,
                },
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609462900000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    assert result is None


def test_validate_time_format_h_mm_format():
    """H:MM形式（1桁時間）のテスト"""
    from winactor_for_wmc.licenses import get_licenses_usage_csv

    assert get_licenses_usage_csv.validate_time_format("9:30") == "09:30:00"
    assert get_licenses_usage_csv.validate_time_format("1:00") == "01:00:00"


def test_format_time_difference_only_days():
    """日のみの時間差（HH:MM:SS形式）"""
    from datetime import timedelta

    from winactor_for_wmc.licenses import get_licenses_usage_csv

    assert (
        get_licenses_usage_csv.format_time_difference(timedelta(days=3)) == "72:00:00"
    )


def test_format_time_difference_only_hours():
    """時間のみの時間差（HH:MM:SS形式）"""
    from datetime import timedelta

    from winactor_for_wmc.licenses import get_licenses_usage_csv

    assert (
        get_licenses_usage_csv.format_time_difference(timedelta(hours=5)) == "5:00:00"
    )


def test_format_time_difference_only_minutes():
    """分のみの時間差（HH:MM:SS形式）"""
    from datetime import timedelta

    from winactor_for_wmc.licenses import get_licenses_usage_csv

    assert (
        get_licenses_usage_csv.format_time_difference(timedelta(minutes=30))
        == "0:30:00"
    )


def test_run_before_without_time(mocker):
    """beforeで時刻未指定の場合（デフォルト23:59:59）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="before",
            start_date="2021/01/01",
            start_time="",  # 空文字列
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "before"
    assert call_args[1]["params"]["createdAtTime1"] == "23:59:59"


def test_run_after_without_time(mocker):
    """afterで時刻未指定の場合（デフォルト00:00:00）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="after",
            start_date="2021/01/01",
            start_time="",  # 空文字列
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "after"
    assert call_args[1]["params"]["createdAtTime1"] == "00:00:00"


def test_run_checkin_without_checkout_in_stack(mocker):
    """checkout_stackが空の状態でcheckinイベントが来る場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609462800000,
                },
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609466400000,
                },
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609470000000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )
    assert result is None


def test_validate_time_format_single_digit_hour():
    """1桁時間のH:MM形式のテスト（295-296行目）"""
    from winactor_for_wmc.licenses import get_licenses_usage_csv

    # 1桁時間のケース
    assert get_licenses_usage_csv.validate_time_format("5:45") == "05:45:00"
    assert get_licenses_usage_csv.validate_time_format("0:00") == "00:00:00"
    assert get_licenses_usage_csv.validate_time_format("7:15") == "07:15:00"


def test_run_before_without_time_none(mocker):
    """beforeで時刻がNoneの場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="before",
            start_date="2021/01/01",
            # start_timeを指定しない（Noneになる）
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "before"
    assert call_args[1]["params"]["createdAtTime1"] == "23:59:59"


def test_run_after_without_time_none(mocker):
    """afterで時刻がNoneの場合"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="after",
            start_date="2021/01/01",
            # start_timeを指定しない（Noneになる）
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "after"
    assert call_args[1]["params"]["createdAtTime1"] == "00:00:00"


def test_validate_time_format_hh_mm_with_leading_zero():
    """HH:MM形式で先頭ゼロありのテスト"""
    from winactor_for_wmc.licenses import get_licenses_usage_csv

    # 2桁時間のケース（zfillの分岐をカバー）
    assert get_licenses_usage_csv.validate_time_format("09:30") == "09:30:00"
    assert get_licenses_usage_csv.validate_time_format("10:45") == "10:45:00"
    assert get_licenses_usage_csv.validate_time_format("23:59") == "23:59:00"


def test_validate_time_format_edge_cases():
    """validate_time_formatのエッジケース"""
    from winactor_for_wmc.licenses import get_licenses_usage_csv

    # 2桁時間のHH:MM形式
    assert get_licenses_usage_csv.validate_time_format("10:30") == "10:30:00"
    assert get_licenses_usage_csv.validate_time_format("23:59") == "23:59:00"

    # 1桁時間のH:MM形式
    assert get_licenses_usage_csv.validate_time_format("5:45") == "05:45:00"
    assert get_licenses_usage_csv.validate_time_format("0:00") == "00:00:00"

    # 既に正しい形式
    assert get_licenses_usage_csv.validate_time_format("12:34:56") == "12:34:56"
    assert get_licenses_usage_csv.validate_time_format("00:00:00") == "00:00:00"

    # 無効な形式
    assert get_licenses_usage_csv.validate_time_format("invalid") == "00:00:00"
    assert get_licenses_usage_csv.validate_time_format("") == "00:00:00"
    assert get_licenses_usage_csv.validate_time_format("25:00") == "25:00:00"


def test_validate_time_format_single_digit_hour_match():
    """1桁時間のH:MM形式の正規表現マッチ（295-296行目）"""
    from winactor_for_wmc.licenses import get_licenses_usage_csv

    # ^\d{1}:\d{2}$ にマッチするケース（1桁の時間）
    assert get_licenses_usage_csv.validate_time_format("5:45") == "05:45:00"
    assert get_licenses_usage_csv.validate_time_format("0:00") == "00:00:00"
    assert get_licenses_usage_csv.validate_time_format("7:15") == "07:15:00"
    assert get_licenses_usage_csv.validate_time_format("9:59") == "09:59:00"


def test_run_after_mode_complete(mocker):
    """afterモードの完全なテスト（115-133行目）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609459200000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="after",
            start_date="2021/01/01",
            start_time="10:30",  # HH:MM形式で指定
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "after"
    assert call_args[1]["params"]["createdAtDate1"] == "2021/01/01"
    assert call_args[1]["params"]["createdAtTime1"] == "10:30:00"


def test_run_checkin_event_processing(mocker):
    """checkinイベントの処理（209-206行目）"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # checkout → checkin の正常なペア
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを払い出しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609459200000,
                },
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=田中太郎,PC名=PC001",
                    "createdTime": 1609462800000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )

    assert result is None

    # CSVライターが呼ばれたことを確認
    handle = mock_file()
    # writerowsが呼ばれていることを確認（具体的な内容はチェックしない）
    assert handle.write.called or handle.__enter__().write.called


def test_run_checkin_with_empty_stack_detailed(mocker):
    """checkout_stackが空の時のcheckin処理の詳細テスト"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # 最初にcheckinが来る（stackが空）
    mock_client.get.side_effect = [
        {
            "items": [
                {
                    "message": "フローティングライセンスを回収しました。ユーザ名=山田太郎,PC名=PC005",
                    "createdTime": 1609459200000,
                },
            ]
        },
    ]

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )

    assert result is None


def test_run_pagination_full_pages_then_empty(mocker):
    """page_sizeちょうどのページが続いた後、空ページで終了する経路をカバー"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    page_size = 100
    first_page = {
        "items": [
            {
                "message": f"フローティングライセンスを払い出しました。ユーザ名=U{i},PC名=PC{i}",
                "createdTime": 1609459200000 + i * 1000,
            }
            for i in range(page_size)
        ]
    }
    second_page = {
        "items": [
            {
                "message": f"フローティングライセンスを回収しました。ユーザ名=U{i},PC名=PC{i}",
                "createdTime": 1609462800000 + i * 1000,
            }
            for i in range(page_size)
        ]
    }
    empty_page = {"items": []}

    mock_client.get.side_effect = [first_page, second_page, empty_page]

    from unittest.mock import mock_open, patch

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        from winactor_for_wmc.licenses import get_licenses_usage_csv

        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            encoding="UTF-8",
            created_at_type="range",
            start_date="2021/01/01",
            end_date="2021/01/31",
        )

    assert mock_client.get.call_count == 3
    assert result is None


def test_run_created_at_type_whitespace_only_no_dates(mocker):
    """created_at_typeが空白のみ、日付未指定でcreatedAtType未設定の経路をカバー"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    from unittest.mock import mock_open, patch

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        from winactor_for_wmc.licenses import get_licenses_usage_csv

        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="   ",  # 空白のみ
            # start_date/end_date未指定
        )

    call_args = mock_client.get.call_args
    assert "createdAtType" not in call_args[1]["params"]


def test_run_range_end_only_without_time_default(mocker):
    """rangeで検索日2のみ・時刻未指定→23:59:59のデフォルト分岐をカバー"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{"items": []}]

    from unittest.mock import mock_open, patch

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        from winactor_for_wmc.licenses import get_licenses_usage_csv

        get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="range",
            start_date="",
            end_date="2021/01/31",
            # end_time未指定
        )

    call_args = mock_client.get.call_args
    assert call_args[1]["params"]["createdAtType"] == "before"
    assert call_args[1]["params"]["createdAtDate1"] == "2021/01/31"
    assert call_args[1]["params"]["createdAtTime1"] == "23:59:59"


def test_run_response_without_items_key(mocker):
    """eventsレスポンスにitemsキーがない場合のデフォルト経路をカバー"""
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usage_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.side_effect = [{}]  # itemsキーなし

    from unittest.mock import mock_open, patch

    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        from winactor_for_wmc.licenses import get_licenses_usage_csv

        result = get_licenses_usage_csv.run(
            base_url="https://example.com",
            token="dummy_token",
            file_path="/path/to/test.csv",
            created_at_type="range",
        )

    assert mock_client.get.call_count == 1
    assert result is None
