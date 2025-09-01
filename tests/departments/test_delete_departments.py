# tests/departments/test_delete_departments.py

import pytest

from winactor_for_wmc.departments import delete_departments


def test_run_calls_delete(mocker):
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.delete_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.delete.return_value = {"result": "OK"}

    result = delete_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_id="dept123",
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.delete.assert_called_once_with("/departments/dept123")
    assert result is None  # runは何も返さない
