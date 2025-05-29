"""tests.setup test_start_stream module"""
from unittest.mock import Mock
import pytest

from src.setup import start_stream

MOCK_STREAMS_URL="https://mock.api/streams"
MOCK_DICT_POST_HEADERS={"Authorization": "Bearer mock"}

def test_start_stream_success(mocker) -> None:
    """tests.setup test_start_stream_success function"""
    mock_response = Mock()
    mock_response.status_code = 204
    mock_response.text = ""
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.post', return_value=mock_response)
    start_stream("some_stream_id",MOCK_STREAMS_URL,MOCK_DICT_POST_HEADERS)

def test_start_stream_fail_verbose(mocker,capsys) -> None:
    """tests.setup test_start_stream_fail_verbose function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Stream not found"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.post', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        start_stream("some_stream_id",MOCK_STREAMS_URL,MOCK_DICT_POST_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        f"[ERROR] Start streams failed. Message: {mock_response.text}\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
