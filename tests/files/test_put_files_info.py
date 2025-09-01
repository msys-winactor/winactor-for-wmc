from winactor_for_wmc.files import put_files_info


def test_run_calls_put_file_update(mocker):
    # WMCApiClient クラスをモック化
    mock_client_class = mocker.patch(
        "winactor_for_wmc.files.put_files_info.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.put.return_value = {"result": "OK"}

    payload = {
        "name": "renamed.txt",
        "fileTag": "tag-001",
        "description": "updated file",
    }

    result = put_files_info.run(
        base_url="https://example.com",
        token="dummy_token",
        file_id="file_001",
        file_data=payload,
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.put.assert_called_once_with("/files/file_001", data=payload)
    assert result == {"result": "OK"}
