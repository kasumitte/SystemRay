import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from ai.assistant import get_AIResponse
from src.metrics import bytes_to_readable
from system.cleaner import clean_files


@pytest.mark.asyncio
@patch("ai.assistant.get_settings_by_key")
@patch("ai.assistant.save_chat_history")
@patch("ai.assistant.httpx.AsyncClient")
async def test_AIResponse(mock_class, mock_save_history, mock_get_settings):
    db_mock = Path("data/history.db")
    api_key = "alkjsdpq0912"

    mock_get_settings.return_value = ("custom_prompt",)
    
    mock_client_instance = MagicMock()
    mock_class.return_value.__aenter__.return_value = mock_client_instance
    
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [{"message": {"content": "response"}}]
    }
    mock_client_instance.post = AsyncMock(return_value=mock_resp)
    
    session_id, text = await get_AIResponse(api_key=api_key, db_path=db_mock, metrics=[], sys_logs=" ", request=" ") # type: ignore
    
    assert isinstance(session_id, str)
    assert text == "response"
    assert mock_save_history.called


@pytest.mark.parametrize("bytes_val, expected", [
    (0, "0.0 KB"),
    (1024, "1.0 KB"),
    (1024*1024*2.5, "2.5 MB"),
    (1024*1024*1024*5.55, "5.55 GB")
])
def test_bytes_to_readable(bytes_val, expected):
    assert bytes_to_readable(bytes_val) == expected


def test_clean_files(tmp_path):
    file1 = tmp_path / "test1.tmp"
    file2 = tmp_path / "test2.tmp"
    file1.write_text("log")
    file2.write_text("data")
    files_to_clean = [str(file1), str(file2)]
    
    assert file1.exists() and file2.exists()
    result = clean_files(files_to_clean)
    
    assert result["stats"][0] == 2
    assert not file1.exists()
    assert not file2.exists()
