from winactor_for_wmc.files import delete_files  # run関数がここにある想定


def test_run_calls_delete(mocker):
    # WMCApiClientクラスをモック化
    mock_client_class = mocker.patch("winactor_for_wmc.files.delete_files.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.delete.return_value = {"result": "OK"}

    result = delete_files.run(
        base_url="https://example.com", token="dummy_token", file_id="file123"
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.delete.assert_called_once_with("/files/file123")
    assert result == {"result": "OK"}  # runはresponseを返している
