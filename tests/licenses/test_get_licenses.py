# tests/licenses/test_get_licenses.py

import pytest

from winactor_for_wmc.licenses import get_licenses


def test_run_calls_get(mocker):
    # WMCApiClient をモック
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"features": [{"name": "dummy"}]}

    result = get_licenses.run(
        base_url="https://example.com",
        token="dummy_token",
    )

    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.get.assert_called_once_with("/licenses")
    assert result == {"features": [{"name": "dummy"}]}


@pytest.mark.parametrize(
    "kwargs",
    [
        {"base_url": None, "token": "t"},
        {"base_url": "", "token": "t"},
        {"base_url": "https://example.com", "token": None},
        {"base_url": "https://example.com", "token": ""},
    ],
)
def test_run_returns_empty_when_missing_base_or_token(mocker, kwargs):
    # WMCApiClient は呼ばれないはず
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses.WMCApiClient"
    )

    result = get_licenses.run(**kwargs)

    assert result == {}
    mock_client_class.assert_not_called()


def test_get_feature_info_picks_correct_index_and_maps_fields():
    # 入力となるAPIレスポンス（簡易）
    result = {
        "features": [
            {
                "name": "フル機能版",
                "licenseType": 0,
                "deathTime": 111,
                "startTime": 101,
                "numLicenses": 10,
                "trialDaysLeft": 0,
                "keyLifeTime": 60,
                "locale": "ja-JP",
            },
            {
                "name": "実行版",
                "licenseType": 1,
                "deathTime": 222,
                "startTime": 202,
                "numLicenses": 20,
                "trialDaysLeft": 5,
                "keyLifeTime": 120,
                "locale": "en-US",
            },
        ]
    }

    # index=1 を指定して2件目が返ることを確認
    info = get_licenses.get_feature_info(result, index=1)

    assert info == {
        "name": "実行版",
        "licenseType": 1,
        "deathTime": 222,
        "startTime": 202,
        "numLicenses": 20,
        "trialDaysLeft": 5,
        "keyLifeTime": 120,
        "locale": "en-US",
    }


def test_get_feature_info_uses_defaults_for_optional_strings():
    # name と locale は get(..., "") なので欠落時は "" になる
    result = {
        "features": [
            {
                # "name" 欠落
                "licenseType": 0,
                "deathTime": 111,
                "startTime": 101,
                "numLicenses": 10,
                "trialDaysLeft": 0,
                "keyLifeTime": 60,
                # "locale" 欠落
            }
        ]
    }

    info = get_licenses.get_feature_info(result, index=0)

    assert info["name"] == ""
    assert info["locale"] == ""
    # 数値フィールドは必須として dict 直アクセスのため、ここでは存在している前提
    assert info["licenseType"] == 0
    assert info["deathTime"] == 111
    assert info["startTime"] == 101
    assert info["numLicenses"] == 10
    assert info["trialDaysLeft"] == 0
    assert info["keyLifeTime"] == 60
