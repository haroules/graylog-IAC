"""tests.setup test_check_extractor_exists module"""
from unittest.mock import Mock
import json
import requests
import pytest


from src.setup import check_extractor_exists
from tests.setup.test_setup_common import create_sample_extractor_config_dir

MOCK_BOOL_VEBOSE=True
MOCK_INPUTS_URL="https://mock.api/inputs"
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_GET_API_RETURN = { "total": 0, "extractors": [] }
MOCK_GET_API_RETURN_EXISTING = { "total": 1, "extractors": [{"title": "xtrctr_title"}] }
MOCK_EXTRACTOR_ID = "extractor_id_string"

def test_check_extractor_exists_success_not_existing(tmp_path,mocker) -> None:
    """tests.setup test_check_extractor_exists_success_not_existing module"""
    create_sample_extractor_config_dir(tmp_path,"config-1")
    config_file=tmp_path.as_posix()+"/config-1/config_0.json"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps(MOCK_GET_API_RETURN)
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    returnval = check_extractor_exists(MOCK_BOOL_VEBOSE,MOCK_EXTRACTOR_ID,config_file,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    assert returnval == ["xtrctr_title"]

def test_check_extractor_exists_success_existing(tmp_path,mocker,capsys) -> None:
    """tests.setup test_check_extractor_exists_success_existing module"""
    create_sample_extractor_config_dir(tmp_path,"config-1")
    config_file=tmp_path.as_posix()+"/config-1/config_0.json"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps(MOCK_GET_API_RETURN_EXISTING)
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    returnval = check_extractor_exists(MOCK_BOOL_VEBOSE,MOCK_EXTRACTOR_ID,config_file,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "     Extractor ['xtrctr_title'] already exists\n"
    )
    assert captured.out == expected_output
    assert returnval is True

def test_check_extractor_exists_fail_filenotfound(tmp_path,mocker,capsys) -> None:
    """tests.setup test_check_extractor_exists_fail_filenotfound module"""
    create_sample_extractor_config_dir(tmp_path,"config-1")
    config_file=tmp_path.as_posix()+"/config-1/non_exist.json"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps(MOCK_GET_API_RETURN_EXISTING)
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', return_value=mock_response)
    with pytest.raises(SystemExit) as e:
        check_extractor_exists(MOCK_BOOL_VEBOSE,MOCK_EXTRACTOR_ID,config_file,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    message = "[ERROR] File or directory not found in check_extractor_exists:"
    expected_output = (
        f"{message} [Errno 2] No such file or directory: '{config_file}'\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1

def test_check_extractor_exists_fail_request_exception(tmp_path,mocker,capsys) -> None:
    """tests.setup test_check_extractor_exists_fail_request_exception module"""
    create_sample_extractor_config_dir(tmp_path,"config-1")
    config_file=tmp_path.as_posix()+"/config-1/config_0.json"
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = json.dumps(MOCK_GET_API_RETURN)
    mock_response.raise_for_status = Mock()
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    with pytest.raises(SystemExit) as e:
        check_extractor_exists(MOCK_BOOL_VEBOSE,MOCK_EXTRACTOR_ID,config_file,MOCK_INPUTS_URL,MOCK_DICT_GET_HEADERS)
    captured = capsys.readouterr()
    expected_output = (
        "[ERROR] Request error in check_extractor_exists: Connection error\n"
    )
    assert captured.out == expected_output
    assert e.value.code == 1
