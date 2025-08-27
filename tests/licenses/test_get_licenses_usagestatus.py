# tests/licenses/test_get_license_info.py

import pytest

from winactor_for_wmc.licenses import get_licenses_usagestatus


def test_run_calls_get_with_allowed_params(mocker):
    # WMCApiClient をモック
    mock_client_class = mocker.patch(
        "winactor_for_wmc.licenses.get_licenses_usagestatus.WMCApiClient"
    )
    mock_client = mock_client_class.return_value
    mock_client.get.return_value = {"licenses": [{"id": "L1"}]}

    # 許可されたパラメータ + 許可されていないパラメータを混在
    kwargs = {
        "base_url": "https://example.com",
        "token": "dummy_token",
        "winactorNameType": "exact",
        "winactorName": "WA-01",
        "pcNameType": "like",
        "pcName": "PC-01",
        "userNameType": "like",
        "userName": "user",
        "licenseGroupNameType": "exact",
        "licenseGroupName": "G1",
        "sort": "userName",
        "sortDirection": "asc",
        "notAllowed": "SHOULD_BE_FILTERED_OUT",
    }

    result = get_licenses_usagestatus.run(**kwargs)

    # クライアント生成と GET 呼び出しの検証
    mock_client_class.assert_called_once_with("https://example.com", "dummy_token")
    mock_client.get.assert_called_once()

    (called_endpoint,) = mock_client.get.call_args[0]
    called_params = mock_client.get.call_args[1]["params"]

    assert called_endpoint == "/licenses"
    assert called_params == {
        "winactorNameType": "exact",
        "winactorName": "WA-01",
        "pcNameType": "like",
        "pcName": "PC-01",
        "userNameType": "like",
        "userName": "user",
        "licenseGroupNameType": "exact",
        "licenseGroupName": "G1",
        "sort": "userName",
        "sortDirection": "asc",
    }
    assert result == {"licenses": [{"id": "L1"}]}


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
        "winactor_for_wmc.licenses.get_licenses_usagestatus.WMCApiClient"
    )

    result = get_licenses_usagestatus.run(**kwargs)

    assert result == {}
    mock_client_class.assert_not_called()


def test_get_license_info_picks_correct_index_and_maps_fields():
    result = {
        "licenses": [
            {
                "id": "L1",
                "userName": "u1",
                "pcName": "pc1",
                "expiration": "170",
                "locale": "ja-JP",
                "featureName": "フル機能版",
                "winactorName": "WA-01",
                "licenseGroupName": "G1",
            },
            {
                "id": "L2",
                "userName": "u2",
                "pcName": "pc2",
                "expiration": 200,
                "locale": "en-US",
                "featureName": "実行版",
                "winactorName": "WA-02",
                "licenseGroupName": "G2",
            },
        ]
    }

    info = get_licenses_usagestatus.get_license_info(result, index=1)

    assert info == {
        "id": "L2",
        "userName": "u2",
        "pcName": "pc2",
        "expiration": 200,
        "locale": "en-US",
        "featureName": "実行版",
        "winactorName": "WA-02",
        "licenseGroupName": "G2",
    }


def test_get_license_info_uses_defaults_and_safe_int():
    # 欠落フィールドは ""、数値化不可は 0 になる
    result = {
        "licenses": [
            {
                # id/userName/pcName/locale/featureName/winactorName/licenseGroupName 欠落
                "expiration": "abc",  # 数値化できない
            }
        ]
    }

    info = get_licenses_usagestatus.get_license_info(result, index=0)

    assert info["id"] == ""
    assert info["userName"] == ""
    assert info["pcName"] == ""
    assert info["locale"] == ""
    assert info["featureName"] == ""
    assert info["winactorName"] == ""
    assert info["licenseGroupName"] == ""
    assert info["expiration"] == 0  # _safe_int により 0


def test_get_license_info_accepts_negative_index():
    result = {
        "licenses": [
            {"id": "L1", "expiration": 10},
            {"id": "L2", "expiration": 20},
        ]
    }

    info = get_licenses_usagestatus.get_license_info(result, index=-1)
    assert info["id"] == "L2"
    assert info["expiration"] == 20


def test_get_license_info_handles_none_entry_as_empty_defaults():
    # licenses 内の要素が None の場合でも {} として扱い、既定値が返る
    result = {"licenses": [None]}

    info = get_licenses_usagestatus.get_license_info(result, index=0)

    assert info == {
        "id": "",
        "userName": "",
        "pcName": "",
        "expiration": 0,
        "locale": "",
        "featureName": "",
        "winactorName": "",
        "licenseGroupName": "",
    }


@pytest.mark.parametrize("bad_index", [None, ""])
def test_get_license_info_raises_when_index_not_provided(bad_index):
    result = {"licenses": [{"id": "L1", "expiration": 1}]}

    with pytest.raises(ValueError) as e:
        get_licenses_usagestatus.get_license_info(result, index=bad_index)

    assert "未指定" in str(e.value)


def test_get_license_info_raises_when_result_not_dict():
    with pytest.raises(ValueError) as e:
        get_licenses_usagestatus.get_license_info([], index=0)

    assert "APIレスポンスが不正" in str(e.value)


@pytest.mark.parametrize(
    "bad_licenses",
    [
        None,
        {},
        "not-a-list",
        [],
    ],
)
def test_get_license_info_raises_when_licenses_missing_or_empty(bad_licenses):
    result = {"licenses": bad_licenses} if bad_licenses is not None else {}
    with pytest.raises(ValueError) as e:
        get_licenses_usagestatus.get_license_info(result, index=0)

    assert "ライセンス情報が存在しません" in str(e.value)


@pytest.mark.parametrize("bad_index", ["x", "1.2"])
def test_get_license_info_raises_when_index_not_numeric(bad_index):
    result = {"licenses": [{"id": "L1", "expiration": 1}]}

    with pytest.raises(ValueError) as e:
        get_licenses_usagestatus.get_license_info(result, index=bad_index)

    assert "数値ではありません" in str(e.value)


@pytest.mark.parametrize("bad_index", [2, -2])
def test_get_license_info_raises_when_index_out_of_range(bad_index):
    result = {"licenses": [{"id": "L1", "expiration": 1}]}

    with pytest.raises(ValueError) as e:
        get_licenses_usagestatus.get_license_info(result, index=bad_index)

    assert "範囲外" in str(e.value)
