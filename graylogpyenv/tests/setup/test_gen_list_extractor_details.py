"""tests.setup test_gen_list_extractor_details module"""
from unittest.mock import Mock
import json
import requests
import pytest

from src.setup import gen_list_extractor_details

MOCK_INPUTS_URL="https://mock.api/indexsets"
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_GET_API_RETURN = {"inputs": [ { "title": "samplehost_title", "global": True,
    "name": "input_samplehost", "id": "input_id_string" } ] }
MOCK_CONFIG_SET={
        "index_config_file":"index_samplehost.json",
        "index_title":"samplehost_title",
        "input_config_file":"input_samplehost.json",
        "input_title":"samplehost_title",
        "extractors_total":1,
        "extractors":[{
            "extractor_config_file" :"extractor.json",
            "extractor_title" : "some_extractor"
        }],
        "stream_config_file":"<replace>",
        "stream_title":"<replace>"
        }

def test_gen_list_extractor_details_success(mocker) -> None:
    """setup test_gen_list_extractor_details_success function"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps(MOCK_GET_API_RETURN)
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    returnval = gen_list_extractor_details(MOCK_CONFIG_SET,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    assert returnval == ["input_id_string", '"samplehost_title"', ["extractor.json"]]

def test_gen_list_extractor_details_fail_non_200_response(mocker,capsys) -> None:
    """setup test_gen_list_extractor_details_fail_non_200_response function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        gen_list_extractor_details(MOCK_CONFIG_SET,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        f"[ERROR] API call to: {MOCK_INPUTS_URL} Failed. Message: {mock_response.text}\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_gen_list_extractor_details_fail_request_exception(mocker,capsys) -> None:
    """setup test_gen_list_extractor_details_fail_request_exception function"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Bad response"
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        gen_list_extractor_details(MOCK_CONFIG_SET,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "[ERROR] Request error in gen_list_extractor_details: Connection error\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
