# test_delete_winactors_with_exclude.py

from winactor_for_wmc.winactors import delete_winactors


def test_run_excludes_then_deletes_with_polling(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.delete_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.put.return_value = None
    mock_client.get.side_effect = [
        {"status": "active"},
        {"status": "exclude"},
    ]
    mock_client.delete.return_value = {"result": "OK"}

    mock_sleep = mocker.patch("winactor_for_wmc.winactors.delete_winactors.sleep")

    result = delete_winactors.run(
        base_url="https://example.com",
        token="dummy_token",
        winactor_id="winactor123",
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.put.assert_called_once_with("/winactors/winactor123/exclude")
    assert mock_client.get.call_count == 2
    mock_client.get.assert_any_call("/winactors/winactor123")
    assert mock_sleep.call_count == 1
    mock_client.delete.assert_called_once_with("/winactors/winactor123")
    assert result == {"result": "OK"}


def test_run_excludes_immediately_then_deletes(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.delete_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.put.return_value = None
    mock_client.get.return_value = {"status": "exclude"}
    mock_client.delete.return_value = {"result": "OK"}

    mock_sleep = mocker.patch("winactor_for_wmc.winactors.delete_winactors.sleep")

    result = delete_winactors.run(
        base_url="https://example.com",
        token="dummy_token",
        winactor_id="winactor123",
    )

    mock_client.put.assert_called_once_with("/winactors/winactor123/exclude")
    mock_client.get.assert_called_once_with("/winactors/winactor123")
    mock_sleep.assert_not_called()
    mock_client.delete.assert_called_once_with("/winactors/winactor123")
    assert result == {"result": "OK"}


def test_run_get_raises_but_still_deletes(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.delete_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.put.return_value = None
    mock_client.get.side_effect = RuntimeError("temporary failure")
    mock_client.delete.return_value = {"result": "OK"}

    mocker.patch("winactor_for_wmc.winactors.delete_winactors.sleep")

    result = delete_winactors.run(
        base_url="https://example.com",
        token="dummy_token",
        winactor_id="winactor123",
    )

    mock_client.put.assert_called_once_with("/winactors/winactor123/exclude")
    assert mock_client.get.call_count >= 1
    mock_client.delete.assert_called_once_with("/winactors/winactor123")
    assert result == {"result": "OK"}


def test_run_polling_times_out_then_deletes(mocker):
    """
    20回のポーリングでも exclude にならないケース。
    例外は起きずにループを走り切り、その後 DELETE が呼ばれることを検証。
    """
    mock_client_class = mocker.patch(
        "winactor_for_wmc.winactors.delete_winactors.WMCApiClient"
    )
    mock_client = mock_client_class.return_value

    mock_client.put.return_value = None
    # 20回すべて active（exclude にならない）
    mock_client.get.side_effect = [{"status": "active"}] * 20
    mock_client.delete.return_value = {"result": "OK"}

    mock_sleep = mocker.patch("winactor_for_wmc.winactors.delete_winactors.sleep")

    result = delete_winactors.run(
        base_url="https://example.com",
        token="dummy_token",
        winactor_id="winactor123",
    )

    mock_client.put.assert_called_once_with("/winactors/winactor123/exclude")
    assert mock_client.get.call_count == 20
    assert mock_sleep.call_count == 20  # 毎回 sleep される
    mock_client.delete.assert_called_once_with("/winactors/winactor123")
    assert result == {"result": "OK"}
