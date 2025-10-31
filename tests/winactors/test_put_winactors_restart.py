import pytest

from winactor_for_wmc.winactors import put_winactors_restart


def test_run_calls_put(mocker):
    # WMCApiClient をモック化
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.put_winactors_restart.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.put.return_value = {"result": "OK"}

    result = put_winactors_restart.run(
        base_url="https://example.com",
        token="dummy_token",
        winactor_id="wa-001",
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.put.assert_called_once_with("/winactors/wa-001/restart")
    assert result is None  # runは何も返さない
