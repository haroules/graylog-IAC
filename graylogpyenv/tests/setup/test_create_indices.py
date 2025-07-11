"""Module:tests.setup.test_create_indices"""
import os
import json
from unittest.mock import patch
import requests
import pytest

from src.setup import create_indices
from tests.common.test_common import create_config_dir
from tests.common.test_common import shared_asserts
from tests.common.test_common import mock_get_response
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import MOCK_STR_INDEXSETS_URL
from tests.common.test_common import MOCK_DICT_POST_HEADERS

CWD = os.getcwd()
INDEXCONFIGDIR = CWD + "/tests/test-configs/indices"
INDEXCONFIGFILE = CWD + "/tests/test-configs/indices/index_samplehost.json"

def test_create_indices_non_exist_verbose_success(mocker,capsys) -> None:
    """Function:test_create_indices_non_exist_verbose_success"""
    config_file_list=[INDEXCONFIGFILE]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        mock_response = mock_get_response(200,json.dumps({"title": "mock_index", "id": "mock_id"}))
        mocker.patch("requests.post", return_value=mock_response)
        create_indices(BOOL_VERBOSE_TRUE,INDEXCONFIGDIR,MOCK_STR_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {INDEXCONFIGFILE}\n"
            "      Index:['mock_index'] Id:['mock_id'] was created\n"
            "[Done] processing indexes.\n\n"
        )
        assert captured.out ==  expected_output

def test_create_indices_already_exist_verbose_success(mocker,capsys) -> None:
    """Function:test_create_indices_already_exist_verbose_success"""
    config_file_list=[INDEXCONFIGFILE]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        mock_response = mock_get_response(400,json.dumps({"title": "mock_index", "id": "mock_id"}))
        mocker.patch("requests.post", return_value=mock_response)
        create_indices(BOOL_VERBOSE_TRUE,INDEXCONFIGDIR,MOCK_STR_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {INDEXCONFIGFILE}\n"
            '      Index already exists:{"title": "mock_index", "id": "mock_id"}\n'
            "[Done] processing indexes.\n\n"
        )
        assert captured.out ==  expected_output

def test_create_indices_fail_post_verbose(mocker,capsys) -> None:
    """Function:test_create_indices_fail_post_verbose"""
    config_file_list=[INDEXCONFIGFILE]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        mock_response = mock_get_response(403,json.dumps({"title": "mock_index", "id": "mock_id"}))
        mocker.patch("requests.post", return_value=mock_response)
        with pytest.raises(SystemExit) as e:
            create_indices(BOOL_VERBOSE_TRUE,INDEXCONFIGDIR,MOCK_STR_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {INDEXCONFIGFILE}\n"
            f"[ERROR] Create index {config_file_list[0]} Message: {mock_response.text}\n"
        )
        shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_indices_fail_file_not_found_verbose(capsys) -> None:
    """Function:test_create_indices_fail_file_not_found_verbose"""
    config_file_list=["bad_path"]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        with pytest.raises(SystemExit) as e:
            create_indices(BOOL_VERBOSE_TRUE,INDEXCONFIGDIR,MOCK_STR_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        message = "[ERROR]: File or directory not found. Couln't open index config file"
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: bad_path\n"
            f"{message} [Errno 2] No such file or directory: '{config_file_list[0]}'\n"
        )
        shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_indices_fail_json_decode_error_verbose(tmp_path,capsys) -> None:
    """Function:test_create_indices_fail_json_decode_error_verbose"""
    config=create_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json"]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        with pytest.raises(SystemExit) as e:
            create_indices(BOOL_VERBOSE_TRUE,config,MOCK_STR_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_0.json"}\n"
            f"[ERROR] There was a problem decoding json in create indices: Expecting value: line 1 column 1 (char 0)\n"
        )
        shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_create_indices_fail_request_exception(capsys) -> None:
    """Function:test_create_indices_fail_request_exception"""
    config_file_list=[INDEXCONFIGFILE]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        with patch('requests.post', side_effect=requests.exceptions.RequestException("Connection error")):
            with pytest.raises(SystemExit) as e:
                create_indices(BOOL_VERBOSE_TRUE,INDEXCONFIGDIR,MOCK_STR_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
            captured = capsys.readouterr()
            expected_output = (
                "Processing indexes\n"
                f"    Creating index from config: {INDEXCONFIGFILE}\n"
                f"[ERROR] Request error in create indices: Connection error\n"
            )
            shared_asserts(captured.out,expected_output,e.value.code,e.type)
