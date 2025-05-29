"""setup test_create_indices module"""
import json
from unittest.mock import patch, Mock
import requests
import pytest

from src.setup import create_indices
from tests.setup.test_setup_common import create_sample_index_config_dir
from tests.setup.test_setup_common import create_bad_sample_index_config_dir

MOCK_INDEXSETS_URL="https://mock.api/indexsets"
MOCK_DICT_POST_HEADERS={"Authorization": "Bearer mock"}
MOCK_DICT_GET_HEADERS={"Authorization": "Bearer mock"}
MOCK_BOOL_VEBOSE=True

def test_create_indices_non_exist_verbose_success(tmp_path,mocker,capsys) -> None:
    """setup test_create_indices_non_exist_verbose_success function"""
    config=create_sample_index_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json",
                      tmp_path.as_posix()+"/config-1/config_1.json"]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        response = Mock()
        response.status_code = 200
        response.text = json.dumps({"title": "mock_index", "id": "mock_id"})
        mocker.patch("requests.post", return_value=response)
        create_indices(MOCK_BOOL_VEBOSE,config,MOCK_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_0.json"}\n"
            "      Index:['mock_index'] Id:['mock_id'] was created\n"
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_1.json"}\n"
            "      Index:['mock_index'] Id:['mock_id'] was created\n"
            "[Done] processing indexes.\n\n"
        )
        assert captured.out ==  expected_output

def test_create_indices_already_exist_verbose_success(tmp_path,mocker,capsys) -> None:
    """setup test_create_indices_already_exist_non_verbose_success function"""
    config=create_sample_index_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json",
                      tmp_path.as_posix()+"/config-1/config_1.json"]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        response = Mock()
        response.status_code = 400
        response.text = json.dumps({"title": "mock_index", "id": "mock_id"})
        mocker.patch("requests.post", return_value=response)
        create_indices(MOCK_BOOL_VEBOSE,config,MOCK_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_0.json"}\n"
            '      Index already exists:{"title": "mock_index", "id": "mock_id"}\n'
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_1.json"}\n"
            '      Index already exists:{"title": "mock_index", "id": "mock_id"}\n'
            "[Done] processing indexes.\n\n"
        )
        assert captured.out ==  expected_output

def test_create_indices_fail_post_verbose(tmp_path,mocker,capsys) -> None:
    """setup test_create_indices_fail_post_verbose function"""
    config=create_sample_index_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json",
                      tmp_path.as_posix()+"/config-1/config_1.json"]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        response = Mock()
        response.status_code = 403
        response.text = json.dumps({"title": "mock_index", "id": "mock_id"})
        mocker.patch("requests.post", return_value=response)
        with pytest.raises(SystemExit) as e:
            create_indices(MOCK_BOOL_VEBOSE,config,MOCK_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_0.json"}\n"
            f"[ERROR] Create index {config_file_list[0]} Message: {response.text}\n"
        )
        assert captured.out ==  expected_output
        assert e.value.code == 1

def test_create_indices_fail_file_not_found_verbose(tmp_path,mocker,capsys) -> None:
    """setup test_create_indices_fail_file_not_found_verbose function"""
    config=create_sample_index_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_3.json"]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
        with pytest.raises(SystemExit) as e:
            create_indices(MOCK_BOOL_VEBOSE,config,MOCK_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        message = "[ERROR]: File or directory not found. Couln't open index config file"
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_3.json"}\n"
            f"{message} [Errno 2] No such file or directory: '{config_file_list[0]}'\n"
        )
        assert captured.out ==  expected_output
        assert e.value.code == 1

def test_create_indices_fail_json_decode_error_verbose(tmp_path,capsys) -> None:
    """setup test_create_indices_fail_json_decode_error_verbose function"""
    config=create_bad_sample_index_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json"]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        with pytest.raises(SystemExit) as e:
            create_indices(MOCK_BOOL_VEBOSE,config,MOCK_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_0.json"}\n"
            f"[ERROR] There was a problem decoding json in create indices: Expecting value: line 1 column 1 (char 0)\n"
        )
        assert captured.out ==  expected_output
        assert e.value.code == 1

def test_create_indices_fail_request_exception(tmp_path,mocker,capsys) -> None:
    """setup test_create_indices_fail_request_exception"""
    config=create_sample_index_config_dir(tmp_path,"config-1")
    config_file_list=[tmp_path.as_posix()+"/config-1/config_0.json"]
    with patch("src.setup.get_list_config_files",return_value=config_file_list):
        mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
        with pytest.raises(SystemExit) as e:
            create_indices(MOCK_BOOL_VEBOSE,config,MOCK_INDEXSETS_URL,MOCK_DICT_POST_HEADERS)
        captured = capsys.readouterr()
        expected_output = (
            "Processing indexes\n"
            f"    Creating index from config: {tmp_path.as_posix()+"/config-1/config_0.json"}\n"
            f"[ERROR] Request error in create indices:"
        )
        assert expected_output in captured.out
        assert e.value.code == 1
