"""Module:tests.verify.test_verify_stream_rules"""
import os
import pytest

from src.verify import verify_stream_rules
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import create_badjson_host_config_dir
from tests.common.test_common import create_stream_config_dir

CWD = os.getcwd()
HOSTCONFIGDIR = CWD + "/tests/test-configs/host-config"
STREAMCONFIGDIR = CWD + "/tests/test-configs/streams"

def test_verify_stream_rules_pass(capsys) -> None:
    """Function:test_verify_stream_rules_pass"""
    verify_stream_rules(BOOL_VERBOSE_TRUE,HOSTCONFIGDIR,STREAMCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        "Checking stream rules have valid input static fields\n"
        f"  Host config: {HOSTCONFIGDIR}/samplehost.json\n"
        "    Checking stream config file: stream_samplehost.json\n"
        "[Done] Checking stream rules have valid input static fields.\n\n"
    )
    assert captured.out == expected_output

def test_verify_stream_rules_fail(tmp_path,capsys) -> None:
    """Function:test_verify_stream_rules_fail"""
    streamconfig=create_stream_config_dir("indexsetid",tmp_path,"config-2")
    with pytest.raises(SystemExit) as e:
        verify_stream_rules(BOOL_VERBOSE_TRUE,HOSTCONFIGDIR,streamconfig)
    captured = capsys.readouterr()
    expected_output = (
        "Checking stream rules have valid input static fields\n"
        f"  Host config: {HOSTCONFIGDIR}/samplehost.json\n"
        "    Checking stream config file: stream_samplehost.json\n"
        "[ERROR] input title samplehost-input != input name in bad_title\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_stream_rules_fail_oserror(tmp_path,capsys) -> None:
    """Function:test_verify_stream_rules_fail_oserror"""
    streamconfig=create_stream_config_dir("indexsetid",tmp_path,"config-2")
    with pytest.raises(SystemExit) as e:
        verify_stream_rules(BOOL_VERBOSE_TRUE,"bad_path",streamconfig)
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in verify_stream_rules:"
    expected_output = (
        "Checking stream rules have valid input static fields\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_stream_rules_fail_jsondecode(tmp_path,capsys) -> None:
    """Function:test_verify_stream_rules_fail_jsondecode"""
    hostconfig=create_badjson_host_config_dir(tmp_path,"config-1")
    streamconfig=create_stream_config_dir("indexsetid",tmp_path,"config-2")
    with pytest.raises(SystemExit) as e:
        verify_stream_rules(BOOL_VERBOSE_TRUE,hostconfig,streamconfig)
    captured = capsys.readouterr()
    message = "[ERROR] Problem decoding json in verify_stream_rules:"
    expected_output = (
        "Checking stream rules have valid input static fields\n"
        f"  Host config: {hostconfig}/config_0.json\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
