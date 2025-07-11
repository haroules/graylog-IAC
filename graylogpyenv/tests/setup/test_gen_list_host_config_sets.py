"""Function:tests.setup.test_gen_list_host_config_sets"""
import os
import pytest

from src.setup import gen_list_host_config_sets
from tests.common.test_common import create_config_dir
from tests.common.test_common import shared_asserts
from tests.common.test_common import MOCK_HOST_DATA
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
HOSTCONFIGDIR = CWD + "/tests/test-configs/host-config"
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"

def test_gen_list_host_config_sets_verbose_success(capsys) -> None:
    """Function:test_gen_list_host_config_sets_verbose_success"""
    return_val=gen_list_host_config_sets(BOOL_VERBOSE_TRUE,HOSTCONFIGDIR,HOSTCONFIGFILE)
    captured = capsys.readouterr()
    assert captured.out == f"  {HOSTCONFIGFILE} has 1 extractors defined\n"
    assert return_val == MOCK_HOST_DATA

def test_gen_list_host_config_sets_fail_filenotfound(capsys) -> None:
    """Function:test_gen_list_host_config_sets_fail_filenotfound"""
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_sets(BOOL_VERBOSE_TRUE,HOSTCONFIGDIR,"bad_file_path")
    captured = capsys.readouterr()
    message = "[ERROR]: File or directory not found in gen_list_host_config_sets:"
    expected_output = f"{message} [Errno 2] No such file or directory: '{HOSTCONFIGDIR}/bad_file_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_gen_list_host_config_sets_fail_json_decode(tmp_path,capsys) -> None:
    """Function:test_gen_list_host_config_sets_fail_json_decode"""
    config=create_config_dir(tmp_path,"config-1")
    path_config_file = tmp_path.as_posix()+"/config-1/config_0.json"
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_sets(BOOL_VERBOSE_TRUE,config,path_config_file)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in gen_list_host_config_sets:"
    expected_output = f"{message} Expecting value: line 1 column 1 (char 0)\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
