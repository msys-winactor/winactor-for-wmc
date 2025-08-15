from winactor_for_wmc.schedules import put_schedules_enable


def test_run_calls_put_enable(mocker):
    # WMCApiClient クラスをモック化
    mock_client_class = mocker.patch(
        "winactor_for_wmc.schedules.put_schedules_enable.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.put.return_value = {"result": "OK"}

    result = put_schedules_enable.run(
        base_url="https://example.com",
        token="dummy_token",
        schedule_id="sched_001",
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.put.assert_called_once_with("/schedules/sched_001/enable")
    assert result is None  # run は何も返していない
