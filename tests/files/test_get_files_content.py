from unittest.mock import MagicMock, patch

import pytest

# テスト対象モジュールを仮に sample_module.py とします
from sample_module import run


@pytest.fixture
def kwargs():
    return {
        "base_url": "http://example.com",
        "token": "dummy-token",
        "file_id": "123",
        "save_path": "/tmp/file.txt",
    }


@patch("sample_module.WMCApiClient")
def test_run_calls_download_file_with_correct_args(mock_client_class, kwargs):
    # モックインスタンスと返り値を設定
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance
    mock_client_instance.download_file.return_value = "downloaded!"

    result = run(**kwargs)

    # インスタンス生成が正しいか
    mock_client_class.assert_called_once_with(kwargs["base_url"], kwargs["token"])

    # download_file呼び出しが正しいか
    mock_client_instance.download_file.assert_called_once_with(
        f"/files/{kwargs['file_id']}/content",
        params=None,
        save_path=kwargs["save_path"],
    )

    # 返り値が正しいか
    assert result == "downloaded!"


@patch("sample_module.WMCApiClient")
def test_run_missing_kwargs(mock_client_class):
    # すべての引数がNoneでもエラーにならないか（Noneで呼ばれるだけ）
    mock_client_instance = MagicMock()
    mock_client_class.return_value = mock_client_instance
    mock_client_instance.download_file.return_value = "ok"

    result = run()
    mock_client_class.assert_called_once_with(None, None)
    mock_client_instance.download_file.assert_called_once_with(
        "/files/None/content", params=None, save_path=None
    )
    assert result == "ok"
