from winactor_for_wmc.schedules import delete_schedules


def test_run_calls_delete(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.schedules.delete_schedules.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.delete.return_value = {"result": "OK"}

    result = delete_schedules.run(
        base_url="https://example.com", token="dummy_token", schedule_id="schedule123"
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.delete.assert_called_once_with("/schedules/schedule123")
    assert result is None  # runは何も返していない
