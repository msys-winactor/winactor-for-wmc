from winactor_for_wmc.tasks import delete_tasks  # run関数がここにある想定


def test_run_calls_delete(mocker):
    # WMCApiClientクラスをモック化
    mock_client_class = mocker.patch("winactor_for_wmc.tasks.delete_tasks.WMCApiClient")
    mock_client = mock_client_class.return_value
    mock_client.delete.return_value = {"result": "OK"}

    result = delete_tasks.run(
        base_url="https://example.com", token="dummy_token", task_id="task123"
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.delete.assert_called_once_with("/tasks/task123")
    assert result is None  # runは何も返していない
