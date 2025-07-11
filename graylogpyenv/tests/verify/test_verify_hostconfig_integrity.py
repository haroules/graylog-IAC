"""Module:tests.verify.test_verify_hostconfig_integrity"""
import os
import pytest

from src.verify import verify_hostconfig_integrity
from tests.common.test_common import create_badcount_host_config_dir
from tests.common.test_common import create_badjson_host_config_dir
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
HOSTCONFIGDIR= CWD + "/tests/test-configs/host-config"

def test_verify_hostconfig_integrity_pass(capsys) -> None:
    """Function:test_verify_hostconfig_integrity_pass"""
    verify_hostconfig_integrity(BOOL_VERBOSE_TRUE,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        f"Checking host configurations data integrity in directory: {HOSTCONFIGDIR}\n"
        f"  Checking host config file: {HOSTCONFIGDIR}/samplehost.json\n"
        f"    1 Unique indexes defined in: {HOSTCONFIGDIR}/samplehost.json\n"
        f"    1 Unique streams defined in: {HOSTCONFIGDIR}/samplehost.json\n"
        f"    1 Unique extractors defined in: {HOSTCONFIGDIR}/samplehost.json\n"
        "[Done] Checking host config file data integrity.\n\n"
    )
    assert captured.out == expected_output

def test_verify_hostconfig_integrity_fail(tmp_path,capsys) -> None:
    """Function:test_verify_hostconfig_integrity_fail"""
    hostconfig=create_badcount_host_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        verify_hostconfig_integrity(BOOL_VERBOSE_TRUE,hostconfig)
    captured = capsys.readouterr()
    expected_output = (
        f"Checking host configurations data integrity in directory: {hostconfig}\n"
        f"  Checking host config file: {hostconfig}/config_0.json\n"
        f"[ERROR] Duplicate indexes in host config file:{hostconfig}/config_0.json\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostconfig_integrity_fail_oserror(capsys) -> None:
    """Function:test_verify_hostconfig_integrity_fail_oserror"""
    with pytest.raises(SystemExit) as e:
        verify_hostconfig_integrity(BOOL_VERBOSE_TRUE,"bad_path")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in verify_hostconfig_integrity:"
    expected_output = (
        "Checking host configurations data integrity in directory: bad_path\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostconfig_integrity_fail_jsondecode(tmp_path,capsys) -> None:
    """Function:test_verify_hostconfig_integrity_fail_jsondecode"""
    hostconfig=create_badjson_host_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        verify_hostconfig_integrity(BOOL_VERBOSE_TRUE,hostconfig)
    captured = capsys.readouterr()
    message = "[ERROR] Problem decoding json in verify_hostconfig_integrity:"
    expected_output = (
        f"Checking host configurations data integrity in directory: {hostconfig}\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
