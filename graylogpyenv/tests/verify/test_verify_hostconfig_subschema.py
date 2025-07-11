"""Module:tests.verify.test_verify_hostconfig_subschema"""
import os
from jsonschema.exceptions import ValidationError
import pytest

from src.verify import verify_hostconfig_subschema
from tests.common.test_common import shared_asserts
from tests.common.test_common import create_badjson_host_config_dir
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
HOSTCONFIGDIR= CWD + "/tests/test-configs/host-config"
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"
SCHEMACONFIGFILE = CWD + "/tests/test-configs/schemas/sample_object_schema.json"

def test_verify_hostconfig_subschema_pass(capsys) -> None:
    """Function:test_verify_hostconfig_subschema_pass"""
    verify_hostconfig_subschema(BOOL_VERBOSE_TRUE,["samplehost.json"],SCHEMACONFIGFILE,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
       "    Verifying object(s): ['samplehost.json']\n"
       f"      Using schema: {SCHEMACONFIGFILE}\n"
       f"      Checking: {HOSTCONFIGFILE}\n"
       "      Object(s) align with schema.\n"
    )
    assert captured.out == expected_output

def test_verify_hostconfig_subschema_fail_oserror(capsys) -> None:
    """Function:test_verify_hostconfig_subschema_fail_oserror"""
    with pytest.raises(SystemExit) as e:
        verify_hostconfig_subschema(BOOL_VERBOSE_TRUE,["config_0.json"],SCHEMACONFIGFILE,"bad_path")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in verify_hostconfig_subschema:"
    expected_output = (
        "    Verifying object(s): ['config_0.json']\n"
       f"      Using schema: {SCHEMACONFIGFILE}\n"
       f"      Checking: bad_path/config_0.json\n"
       f"{message} [Errno 2] No such file or directory: 'bad_path/config_0.json'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostconfig_subschema_fail_jsondecode(tmp_path,capsys) -> None:
    """Function:test_verify_hostconfig_subschema_fail_jsondecode"""
    hostconfig=create_badjson_host_config_dir(tmp_path,"config-1")
    hostfile = tmp_path.as_posix()+"/config-1/config_0.json"
    with pytest.raises(SystemExit) as e:
        verify_hostconfig_subschema(BOOL_VERBOSE_TRUE,["config_0.json"],SCHEMACONFIGFILE,hostconfig)
    captured = capsys.readouterr()
    message = "[ERROR] Problem decoding json in verify_hostconfig_subschema:"
    expected_output = (
       "    Verifying object(s): ['config_0.json']\n"
       f"      Using schema: {SCHEMACONFIGFILE}\n"
       f"      Checking: {hostfile}\n"
       f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostconfig_subschema_fail_validationerror(mocker,capsys) -> None:
    """Function:test_verify_hostconfig_subschema_fail_validationerror"""
    mocker.patch('src.verify.validate', side_effect=ValidationError("Failed Validation"))
    with pytest.raises(SystemExit) as e:
        verify_hostconfig_subschema(BOOL_VERBOSE_TRUE,["samplehost.json"],SCHEMACONFIGFILE,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
       "    Verifying object(s): ['samplehost.json']\n"
       f"      Using schema: {SCHEMACONFIGFILE}\n"
       f"      Checking: {HOSTCONFIGFILE}\n"
       "[ERROR] Doesn't pass schema test in verify_hostconfig_subschema: Failed Validation\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
