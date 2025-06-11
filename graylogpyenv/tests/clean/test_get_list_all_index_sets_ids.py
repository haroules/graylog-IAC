"""tests.clean test_get_list_all_index_sets_ids module"""
import json
from unittest.mock import Mock
import pytest

from src.clean import get_list_all_index_sets_ids

MOCK_JQ_RETURN = ['index1', 'index2']
MOCK_STR_INDEXSETS_URL = "http://test-url.com/index_sets"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}

def test_get_list_all_index_sets_ids_pass(mocker) -> None:
    """tests.clean.test_get_list_all_index_sets_ids_pass function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"indexes": [{"id": "index1"}, {"id": "index2"}]}'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    result = get_list_all_index_sets_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    assert result == ['index1', 'index2']

def test_get_list_all_index_sets_ids_non_200_response_fail(mocker) -> None:
    """tests.clean.test_get_list_all_index_sets_ids_non_200_response_fail function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = '{"indexes": [{"id": "index1"}, {"id": "index2"}]}'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    with pytest.raises(SystemExit) as e:
        get_list_all_index_sets_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS)
    assert e.type == SystemExit
    assert e.value.code == 1
