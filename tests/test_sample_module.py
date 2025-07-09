from template_python import sample_module


def test_run_success():
    result = sample_module.run(user_id="test_user", password="test_password")
    assert result is not None
    assert result["status"] == "success"
    assert "token" in result
    assert result["token"] == "dummy_token_for_test_user"


def test_run_missing_user_id():
    result = sample_module.run(password="test_password")
    assert result is not None
    assert result["status"] == "error"
    assert result["message"] == "ユーザーIDが指定されていません。"


def test_run_missing_password():
    result = sample_module.run(user_id="test_user")
    assert result is not None
    assert result["status"] == "error"
    assert result["message"] == "パスワードが指定されていません。"


def test_run_invalid_arguments():
    result = sample_module.run()
    assert result is not None
    assert result["status"] == "error"
    assert result["message"] == "ユーザーIDが指定されていません。"
