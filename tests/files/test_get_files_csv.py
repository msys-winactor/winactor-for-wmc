from winactor_for_wmc.files import get_files_csv


def test_run_calls_get_csv(mocker):
    # WMCApiClientクラスをモック化
    mock_client_class = mocker.patch(
        "winactor_for_wmc.files.get_files_csv.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get_csv.return_value = None  # get_csvの返り値はrunでは使われない

    # テスト用の引数
    kwargs = {
        "base_url": "https://example.com",
        "token": "dummy_token",
        "save_path": "/tmp/test.csv",
        "params": {"foo": "bar"},
    }

    # run関数を呼ぶ
    result = get_files_csv.run(**kwargs)

    # インスタンス生成とメソッド呼び出しを検証
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.get_csv.assert_called_once_with(
        "/files/csv", params={"foo": "bar"}, save_path="/tmp/test.csv"
    )
    assert result is None  # runは何も返していない
