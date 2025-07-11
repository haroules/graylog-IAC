"""Module:tests.setup.test_gen_list_host_config_files"""
import os
import pytest

from src.setup import gen_list_host_config_files
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import shared_asserts


CWD = os.getcwd()
HOSTCONFIGDIR = CWD + "/tests/test-configs/host-config"
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"

def test_gen_list_host_config_files_success(capsys) -> None:
    """Function:test_gen_list_host_config_files_success"""
    return_value = gen_list_host_config_files(BOOL_VERBOSE_TRUE,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = f"  Adding host config to list:{HOSTCONFIGFILE}\n"
    assert captured.out == expected_output
    assert return_value == [HOSTCONFIGFILE]

def test_gen_list_host_config_files_fail_oserrror(capsys) -> None:
    """Function:test_gen_list_host_config_files_fail_oserrror"""
    with pytest.raises(SystemExit) as e:
        gen_list_host_config_files(BOOL_VERBOSE_TRUE,"bad_path")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in gen_list_host_config_files:"
    expected_output = f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
