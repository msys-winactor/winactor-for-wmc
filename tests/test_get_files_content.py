import os

import pytest

from winactor_for_wmc import get_files_content


def test_download_file_content_success(mocker, tmp_path):
    # テスト用保存先ファイル
    test_file = tmp_path / "downloaded.txt"

    class MockResponse:
        status_code = 200
        content = b"hello world"

        def json(self):
            return {"dummy": "dummy"}

    mocker.patch(
        "winactor_for_wmc.get_files_content.requests.get",
        return_value=MockResponse(),
    )

    result = get_files_content.download_file_content(
        "http://dummy/files", "token", "fileid123", str(test_file)
    )
    # ファイルが正しく保存されたか
    assert result == str(test_file)
    with open(test_file, "rb") as f:
        assert f.read() == b"hello world"


def test_download_file_content_api_error_json(mocker, tmp_path):
    test_file = tmp_path / "downloaded.txt"

    class MockResponse:
        status_code = 404

        def json(self):
            return {"error": "NotFound", "detail": "ファイルがありません"}

    mocker.patch(
        "winactor_for_wmc.get_files_content.requests.get",
        return_value=MockResponse(),
    )

    with pytest.raises(get_files_content.DownloadFileError) as excinfo:
        get_files_content.download_file_content(
            "http://dummy/files", "token", "fileid123", str(test_file)
        )
    assert "status_code: 404" in str(excinfo.value)
    assert "NotFound" in str(excinfo.value)


def test_download_file_content_api_error_json_decode(mocker, tmp_path):
    test_file = tmp_path / "downloaded.txt"

    class MockResponse:
        status_code = 403

        def json(self):
            raise Exception("json decode error")

    mocker.patch(
        "winactor_for_wmc.get_files_content.requests.get",
        return_value=MockResponse(),
    )

    with pytest.raises(get_files_content.DownloadFileError) as excinfo:
        get_files_content.download_file_content(
            "http://dummy/files", "token", "fileid123", str(test_file)
        )
    assert "status_code: 403" in str(excinfo.value)


def test_download_file_content_requests_exception(mocker, tmp_path):
    test_file = tmp_path / "downloaded.txt"

    mocker.patch(
        "winactor_for_wmc.get_files_content.requests.get",
        side_effect=Exception("network error"),
    )

    with pytest.raises(get_files_content.DownloadFileError) as excinfo:
        get_files_content.download_file_content(
            "http://dummy/files", "token", "fileid123", str(test_file)
        )
    assert "network error" in str(excinfo.value)


def test_download_file_content_save_file_error(mocker, tmp_path):
    # 保存先がディレクトリ（書き込み失敗を発生させる）
    test_dir = tmp_path / "dir"
    test_dir.mkdir()

    class MockResponse:
        status_code = 200
        content = b"hello world"

        def json(self):
            return {}

    mocker.patch(
        "winactor_for_wmc.get_files_content.requests.get",
        return_value=MockResponse(),
    )

    # ディレクトリにファイルとして書き込もうとするのでOSError
    with pytest.raises(get_files_content.DownloadFileError):
        get_files_content.download_file_content(
            "http://dummy/files", "token", "fileid123", str(test_dir)
        )
