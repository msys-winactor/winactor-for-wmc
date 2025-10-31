# tests/departments/test_put_departments.py

import pytest

from winactor_for_wmc.departments import put_departments


def test_run_calls_put_department_update(mocker):
    # WMCApiClient クラスをモック化
    mock_client_class = mocker.patch(
        "winactor_for_wmc.departments.put_departments.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.put.return_value = {"result": "OK"}

    payload = {
        "name": "新しい所属名",
        "remarks": "備考を更新しました",
    }

    result = put_departments.run(
        base_url="https://example.com",
        token="dummy_token",
        department_id="dep_001",
        department_data=payload,
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.put.assert_called_once_with("/departments/dep_001", data=payload)
    assert result == {"result": "OK"}
