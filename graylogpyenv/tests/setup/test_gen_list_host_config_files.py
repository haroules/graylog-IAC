"""tests.setup test_gen_list_host_config_files module"""
import pytest

from src.setup import gen_list_host_config_files
from tests.common.test_common import create_sample_host_config_dir
from tests.common.test_common import shared_asserts

MOCK_BOOL_VERBOSE=True

def test_gen_list_host_config_files_success(tmp_path,capsys) -> None:
    """tests.setup.test_gen_list_host_config_files_success function"""
    hostconfig=create_sample_host_config_dir(tmp_path,"config-1")
    hostconfigfile_path = tmp_path.as_posix()+"/config-1/config_0.json"
    return_value = gen_list_host_config_files(MOCK_BOOL_VERBOSE,hostconfig)
    captured = capsys.readouterr()
    expected_output = f"  Adding host config to list:{hostconfigfile_path}\n"
    assert captured.out == expected_output
    assert return_value == [hostconfigfile_path]

def test_gen_list_host_config_files_fail_oserrror(capsys) -> None:
    """tests.setup.test_gen_list_host_config_files_fail_oserrror function"""
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_files(MOCK_BOOL_VERBOSE,"bad_path")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in gen_list_host_config_files:"
    expected_output = f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
