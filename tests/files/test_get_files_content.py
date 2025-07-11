import pytest

from winactor_for_wmc.files import get_files_content


def test_run_normal(mocker):
    # ここを修正！
    mock_client_class = mocker.patch(
        "winactor_for_wmc.files.get_files_content.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.download_file.return_value = "success"

    kwargs = {
        "base_url": "http://example.com",
        "token": "TOKEN",
        "file_id": "FILEID",
        "save_path": "/tmp/test.txt",
    }
    result = get_files_content.run(**kwargs)

    mock_client_class.assert_called_once_with("http://example.com", "TOKEN")
    mock_client.download_file.assert_called_once_with(
        "/files/FILEID/content", params=None, save_path="/tmp/test.txt"
    )
    assert result == "success"


def test_run_all_none(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.files.get_files_content.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.download_file.return_value = "none_result"

    kwargs = {}
    result = get_files_content.run(**kwargs)

    mock_client_class.assert_called_once_with(None, None)
    mock_client.download_file.assert_called_once_with(
        "/files/None/content", params=None, save_path=None
    )
    assert result == "none_result"


def test_run_download_file_exception(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.files.get_files_content.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.download_file.side_effect = RuntimeError("download error")

    kwargs = {
        "base_url": "http://example.com",
        "token": "TOKEN",
        "file_id": "FILEID",
        "save_path": "/tmp/test.txt",
    }
    with pytest.raises(RuntimeError, match="download error"):
        get_files_content.run(**kwargs)
