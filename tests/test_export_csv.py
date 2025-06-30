import pytest

from winactor_for_wmc import export_csv


def test_export_csv_success(mocker, tmp_path):
    # 正常系: status_code=200, ファイル書き込み
    class MockResponse:
        status_code = 200
        content = b"csv,data,here"

    mocker.patch(
        "winactor_for_wmc.export_csv.requests.get", return_value=MockResponse()
    )
    save_path = tmp_path / "test.csv"
    ret = export_csv.export_csv(
        "http://dummy/csv", "token", {}, save_path=str(save_path)
    )
    assert ret == str(save_path)
    # ファイルができている
    assert save_path.read_bytes() == b"csv,data,here"


def test_export_csv_api_error_json(mocker):
    # 異常系: status_code!=200 で json()は正常
    class MockResponse:
        status_code = 400

        def json(self):
            return {"error": "Bad", "detail": "詳細"}

    mocker.patch(
        "winactor_for_wmc.export_csv.requests.get", return_value=MockResponse()
    )
    with pytest.raises(export_csv.ExportCsvError) as excinfo:
        export_csv.export_csv("http://dummy/csv", "token", {}, "dummy.csv")
    assert "status_code: 400" in str(excinfo.value)
    assert "Bad" in str(excinfo.value)
    assert "詳細" in str(excinfo.value)


def test_export_csv_api_error_json_decode(mocker):
    # 異常系: status_code!=200 で json()が例外
    class MockResponse:
        status_code = 404

        def json(self):
            raise Exception("json decode error")

    mocker.patch(
        "winactor_for_wmc.export_csv.requests.get", return_value=MockResponse()
    )
    with pytest.raises(export_csv.ExportCsvError) as excinfo:
        export_csv.export_csv("http://dummy/csv", "token", {}, "dummy.csv")
    assert "status_code: 404" in str(excinfo.value)


def test_export_csv_requests_exception(mocker):
    # requests.get自体が例外
    mocker.patch(
        "winactor_for_wmc.export_csv.requests.get",
        side_effect=Exception("network error"),
    )
    with pytest.raises(export_csv.ExportCsvError) as excinfo:
        export_csv.export_csv("http://dummy/csv", "token", {}, "dummy.csv")
    assert "network error" in str(excinfo.value)


def test_export_csv_file_write_exception(mocker, tmp_path):
    # open/writeで例外（ディレクトリをファイル名に指定して失敗させる）
    class MockResponse:
        status_code = 200
        content = b"abc"

    mocker.patch(
        "winactor_for_wmc.export_csv.requests.get", return_value=MockResponse()
    )
    # ディレクトリをファイル名に渡すことでopenが失敗
    with pytest.raises(export_csv.ExportCsvError):
        export_csv.export_csv("http://dummy/csv", "token", {}, save_path=str(tmp_path))
