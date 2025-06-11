"""tests.setup test_gen_list_host_config_sets module"""
import pytest

import tests.common.test_common
from src.setup import gen_list_host_config_sets
from tests.setup.test_setup_common import create_bad_config_dir
from tests.common.test_common import shared_asserts

MOCK_BOOL_VEBOSE=True

def test_gen_list_host_config_sets_verbose_success(tmp_path,capsys) -> None:
    """tests.setup.test_gen_list_host_config_sets_verbose_success function"""
    config=tests.common.test_common.create_sample_host_config_dir(tmp_path,"config-1")
    path_config_file = tmp_path.as_posix()+"/config-1/config_0.json"
    return_val=gen_list_host_config_sets(MOCK_BOOL_VEBOSE,config,path_config_file)
    captured = capsys.readouterr()
    assert captured.out == f"  {path_config_file} has 1 extractors defined\n"
    assert return_val == tests.common.test_common.MOCK_HOST_DATA

def test_gen_list_host_config_sets_fail_filenotfound(tmp_path,capsys) -> None:
    """tests.setup.test_gen_list_host_config_sets_fail_filenotfound function"""
    config=tests.common.test_common.create_sample_host_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_sets(MOCK_BOOL_VEBOSE,config,"bad_file_path")
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in gen_list_host_config_sets:"
    expected_output = f"{message} [Errno 2] No such file or directory: '{config}/bad_file_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_host_config_sets_fail_json_decode(tmp_path,capsys) -> None:
    """tests.setup.test_gen_list_host_config_sets_fail_json_decode function"""
    config=create_bad_config_dir(tmp_path,"config-1")
    path_config_file = tmp_path.as_posix()+"/config-1/config_0.json"
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_sets(MOCK_BOOL_VEBOSE,config,path_config_file)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_host_config_sets:"
    expected_output = f"{message} Expecting value: line 1 column 1 (char 0)\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
