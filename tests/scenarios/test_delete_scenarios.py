from winactor_for_wmc.scenarios import delete_scenarios  # run関数がここにある想定


def test_run_calls_delete(mocker):
    # WMCApiClientクラスをモック化
    mock_client_class = mocker.patch(
        "winactor_for_wmc.scenarios.delete_scenarios.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.delete.return_value = {"result": "OK"}

    result = delete_scenarios.run(
        base_url="https://example.com", token="dummy_token", scenario_id="scenario123"
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.delete.assert_called_once_with("/scenarios/scenario123")
    assert result is None  # runは何も返していない
