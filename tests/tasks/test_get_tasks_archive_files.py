import pytest

from winactor_for_wmc.tasks import get_tasks_archive_files


def test_run_success(mocker):
    # モックの用意
    mock_client_class = mocker.patch(
        "winactor_for_wmc.tasks.get_tasks_archive_files.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    # モックで返すレスポンス
    mock_response = {
        "total": 2,
        "items": [
            {
                "createdTime": 1753768260071,
                "archiveFileId": "abc123",
                "archiveFileName": "sample1.zip",
            },
            {
                "createdTime": 1753768269999,
                "archiveFileId": "def456",
                "archiveFileName": "sample2.zip",
            },
        ],
    }
    mock_client.get.return_value = mock_response

    # テスト実行
    base_url = "https://example.com"
    token = "dummy_token"
    task_id = "test_task_id"

    result = get_tasks_archive_files.run(
        base_url=base_url, token=token, task_id=task_id
    )

    # 検証
    mock_client_class.assert_called_once_with(base_url, token)
    mock_client.get.assert_called_once_with(f"/tasks/{task_id}/archive-files")
    assert result == mock_response
