"""clean test_gen_list_index_set_names_to_delete module"""
import json
from unittest.mock import Mock
import requests
import pytest
from src.clean import gen_list_index_set_names_to_delete

MOCK_JQ_RETURN = ["index1"]
MOCK_STR_INDEXSETS_URL = "http://test-url.com/index_sets"
MOCK_DICT_GET_HEADERS = {"Authorization": "Bearer token"}
MOCK_LIST_INDEX_SET_IDS_TO_DELETE = ["0001"]

@pytest.fixture(autouse=True)
def patch_common_dependencies(mocker) -> None:
    """clean patch_common_dependencies function"""
    mocker.patch('src.clean.jq', return_value=MOCK_JQ_RETURN)

def test_gen_list_index_set_names_to_delete_pass(mocker) -> None:
    """clean test_gen_list_index_set_names_to_delete_pass function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '{"title": "index1"}'
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    mocker.patch('json.loads', return_value=json.loads(mock_response.text))
    result = gen_list_index_set_names_to_delete( MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_LIST_INDEX_SET_IDS_TO_DELETE)
    assert result == ['index1']

@pytest.mark.parametrize(
    "requests_get_behavior,json_loads_behavior,expected_output,exit_code",
    [
        (   # Case: non-200 response
            lambda: Mock(status_code=404, text='{"title": "index1"}', raise_for_status=Mock()),
            json.loads('{"title": "index1"}'),
            "[ERROR] Couldn't find id. 0001\n",
            pytest.raises(SystemExit),
        ),
        (   # Case: RequestException
            requests.exceptions.RequestException("Connection error"),
            None,
            None,
            1,
        ),
        (   # Case: JSON decode error
            lambda: Mock(status_code=200, text='invalid json', raise_for_status=Mock()),
            lambda text: (_ for _ in ()).throw(ValueError("Decoding error")),
            None,
            1,
        ),
    ]
)
def test_gen_list_index_set_names_to_delete_failures(
    mocker, capsys, requests_get_behavior, json_loads_behavior,
    expected_output, exit_code) -> None:
    """clean test_gen_list_index_set_names_to_delete_failures function"""
    if isinstance(requests_get_behavior, Exception):
        mocker.patch('requests.get', side_effect=requests_get_behavior)
    else:
        mock_response = requests_get_behavior()
        mocker.patch('requests.get', return_value=mock_response)
    if json_loads_behavior:
        mocker.patch('json.loads', side_effect=json_loads_behavior)
    if isinstance(exit_code, int):
        mock_exit = mocker.patch('sys.exit')
        gen_list_index_set_names_to_delete(MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_LIST_INDEX_SET_IDS_TO_DELETE)
        mock_exit.assert_called_once_with(exit_code)
    else:
        with exit_code:  # Expected to be pytest.raises(SystemExit)
            gen_list_index_set_names_to_delete(MOCK_STR_INDEXSETS_URL,MOCK_DICT_GET_HEADERS,MOCK_LIST_INDEX_SET_IDS_TO_DELETE)
        captured = capsys.readouterr()
        assert captured.out == expected_output
