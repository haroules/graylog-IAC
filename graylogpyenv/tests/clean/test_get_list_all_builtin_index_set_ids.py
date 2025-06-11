"""tests.clean test_get_list_all_builtin_index_set_ids module"""
import json
from unittest.mock import Mock
import pytest

from src.clean import get_list_all_builtin_index_set_ids

MOCK_JQ_RETURN = ['0001']
MOCK_STR_INDEXSETS_URL = "http://test-url.com/index_sets"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}
MOCK_LIST_BUILTIN_INDEX_SET_NAMES = ["index1", "index2", "index3"]

def test_get_list_all_builtin_index_set_ids_pass(mocker ) -> None:
    """tests.clean.test_get_list_all_builtin_index_set_ids_pass function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"index_sets": [{"id": "0001","title": "index1"}]}'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    result = get_list_all_builtin_index_set_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS, ["index1"])
    assert result == ['0001']

def test_get_list_all_builtin_index_set_ids_non_200_response_fail(mocker) -> None:
    """tests.clean.test_get_list_all_builtin_index_set_ids_non_200_response_fail function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = '{"index_sets": [{"id": "0001","title": "index1"}]}'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)
    with pytest.raises(SystemExit) as e:
        get_list_all_builtin_index_set_ids(MOCK_STR_INDEXSETS_URL, MOCK_DICT_GET_HEADERS, ["index1"])
    assert e.type == SystemExit
    assert e.value.code == 1
