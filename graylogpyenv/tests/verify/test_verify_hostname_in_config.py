"""Module:tests.verify.test_verify_hostname_in_config"""
import os
import pytest

from src.verify import verify_hostname_in_config
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import create_badjson_host_config_dir



def test_verify_hostname_in_config_pass(capsys) -> None:
    """Function:test_verify_hostname_in_config_pass"""
    cwd = os.getcwd()
    hostconfigdir= cwd + "/tests/test-configs/host-config"
    verify_hostname_in_config(BOOL_VERBOSE_TRUE,hostconfigdir)
    captured = capsys.readouterr()
    expected_output = (
        "Checking hostname is present in object filenames and titles\n"
        "  Checking host config: samplehost.json contains: samplehost\n"
        "    Checking index title\n"
        "    Checking input title\n"
        "    Checking stream title\n"
        "    Checking extractor title(s)\n"
        "[Done] Checking hostname is present in object filenames and titles.\n\n"
    )
    assert captured.out == expected_output

def test_verify_hostname_in_config_fail_oserror(capsys) -> None:
    """Function:test_verify_hostname_in_config_fail_oserror"""
    with pytest.raises(SystemExit) as e:
        verify_hostname_in_config(BOOL_VERBOSE_TRUE,"bad_path")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in verify_hostname_in_config:"
    expected_output = (
        "Checking hostname is present in object filenames and titles\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostname_in_config_fail_jsondecode(tmp_path,capsys) -> None:
    """Function:test_verify_hostname_in_config_fail_jsondecode"""
    hostconfigdir=create_badjson_host_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        verify_hostname_in_config(BOOL_VERBOSE_TRUE,hostconfigdir)
    captured = capsys.readouterr()
    message = "[ERROR] Problem decoding json in verify_hostname_in_config:"
    expected_output = (
        "Checking hostname is present in object filenames and titles\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
