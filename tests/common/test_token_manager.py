import json
import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from winactor_for_wmc.common.token_manager import TokenManager, get_token_path


@pytest.fixture
def temp_appdata(monkeypatch):
    temp_dir = tempfile.mkdtemp()
    monkeypatch.setenv("APPDATA", temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_token_save_and_load(temp_appdata):
    base_url = "https://example.com"
    user_id = "testuser"
    token_data = {"token": "abc123"}

    tm = TokenManager(base_url, user_id)
    tm.save_token(token_data)

    tm2 = TokenManager(base_url, user_id)
    loaded_token = tm2.load_token()
    assert loaded_token == "abc123"


def test_get_token_from_cache(temp_appdata):
    base_url = "https://example.com"
    user_id = "cacheduser"
    token_data = {"token": "cached-token"}

    tm = TokenManager(base_url, user_id)
    tm.save_token(token_data)
    token = tm.get_token()
    assert token == "cached-token"


@patch("winactor_for_wmc.common.token_manager.requests.post")
def test_login_and_save_token(mock_post, temp_appdata):
    base_url = "https://example.com"
    user_id = "apiuser"
    password = "secret"
    token_data = {"token": "new-token"}

    mock_response = MagicMock()
    mock_response.json.return_value = token_data
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    tm = TokenManager(base_url, user_id)
    token = tm.get_token(password=password)

    assert token == "new-token"
    path = get_token_path(base_url, user_id)
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        saved = json.load(f)
    assert saved == token_data
