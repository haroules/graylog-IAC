"""Module:tests.verify.test_verify_hostconfigfiles_schema"""
import os
from jsonschema.exceptions import ValidationError
import pytest

from src.verify import verify_hostconfigfiles_schema
from tests.common.test_common import shared_asserts
from tests.common.test_common import create_badcount_host_config_dir
from tests.common.test_common import create_badjson_host_config_dir
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
HOSTCONFIGDIR = CWD + "/tests/test-configs/host-config"
SCHEMACONFIGFILE = CWD + "/tests/test-configs/schemas/sample_object_schema.json"
SCHEMACONFIGNOTJSON = CWD + "/tests/test-configs/schemas/sample_object_text.json"

def test_verify_hostconfigfiles_schema_pass(capsys) -> None:
    """Function:test_verify_hostconfigfiles_schema_pass"""
    verify_hostconfigfiles_schema(BOOL_VERBOSE_TRUE, HOSTCONFIGDIR, SCHEMACONFIGFILE)
    captured = capsys.readouterr()
    expected_output = (
        "Verifying schema of host configuration files.\n"
        f"  Host config directory: {HOSTCONFIGDIR}\n"
        f"  Schema file: {SCHEMACONFIGFILE}\n"
        "  1 host config files found\n"
        f"    Verifying schema of host config: {HOSTCONFIGDIR}/samplehost.json\n"
        f"     1 config sets verified for host: \"samplehost.local.net\"\n"
        "[Done] Verifying schema of host configuration files\n\n"
    )
    assert captured.out == expected_output

def test_verify_hostconfigfiles_schema_fail_configcount(tmp_path,capsys) -> None:
    """Function:test_verify_hostconfigfiles_schema_fail_configcount"""
    hostconfig=create_badcount_host_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        verify_hostconfigfiles_schema(BOOL_VERBOSE_TRUE, hostconfig, SCHEMACONFIGFILE)
    captured = capsys.readouterr()
    expected_output = (
        "Verifying schema of host configuration files.\n"
        f"  Host config directory: {hostconfig}\n"
        f"  Schema file: {SCHEMACONFIGFILE}\n"
        "  1 host config files found\n"
        f"    Verifying schema of host config: {hostconfig}/config_0.json\n"
        "[ERROR] Config sets declared:2 Found:1\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostconfigfiles_schema_fail_oserror(capsys) -> None:
    """Function:test_verify_hostconfigfiles_schema_fail_oserror"""
    with pytest.raises(SystemExit) as e:
        verify_hostconfigfiles_schema(BOOL_VERBOSE_TRUE, "bad_path", "bad_path")
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in verify_hostconfigfiles_schema:"
    expected_output = (
        "Verifying schema of host configuration files.\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostconfigfiles_schema_fail_validationerror(mocker,capsys) -> None:
    """Function:test_verify_hostconfigfiles_schema_fail_validationerror"""
    mocker.patch('src.verify.validate', side_effect=ValidationError("Failed Validation"))
    with pytest.raises(SystemExit) as e:
        verify_hostconfigfiles_schema(BOOL_VERBOSE_TRUE, HOSTCONFIGDIR, SCHEMACONFIGFILE)
    captured = capsys.readouterr()
    expected_output = (
        "Verifying schema of host configuration files.\n"
        f"  Host config directory: {HOSTCONFIGDIR}\n"
        f"  Schema file: {SCHEMACONFIGFILE}\n"
        "  1 host config files found\n"
        f"    Verifying schema of host config: {HOSTCONFIGDIR}/samplehost.json\n"
        "[ERROR] Host config doesn't pass schema test: Failed Validation\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostconfigfiles_schema_fail_jsondecode(tmp_path,capsys) -> None:
    """Function:test_verify_hostconfigfiles_schema_fail_jsondecode"""
    hostconfig=create_badjson_host_config_dir(tmp_path,"config-1")
    with pytest.raises(SystemExit) as e:
        verify_hostconfigfiles_schema(BOOL_VERBOSE_TRUE, hostconfig, SCHEMACONFIGNOTJSON)
    captured = capsys.readouterr()
    message = "[ERROR] There was a problem decoding json in verify_hostconfigfiles_schema:"
    expected_output = (
        "Verifying schema of host configuration files.\n"
        f"  Host config directory: {hostconfig}\n"
        f"  Schema file: {SCHEMACONFIGNOTJSON}\n"
        "  1 host config files found\n"
        f"    Verifying schema of host config: {hostconfig}/config_0.json\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
