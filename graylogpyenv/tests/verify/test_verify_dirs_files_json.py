"""Module:tests.verify.test_verify_dirs_files_json"""
import os
from pathlib import Path
import pytest

from src.verify import verify_dirs_files_json
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE
from tests.common.test_common import validating_outs

CWD = os.getcwd()
CONFIGTESTDATA = CWD + "/tests/test-configs"
HOSTCONFIGDIR= CONFIGTESTDATA + "/host-config"
HOSTTEMPLATEDIR = CONFIGTESTDATA + "/hosttemplate"
HOSTTEMPLATEDIRJSON = CONFIGTESTDATA + "/hosttemplatejson"
HOSTTEMPLATEFILEJSON = CONFIGTESTDATA + "/hosttemplatejson/samplehost.json"
INDEXCONFIGDIR = CONFIGTESTDATA + "/indices"
INPUTCONFIGDIR = CONFIGTESTDATA + "/inputs"
STREAMCONFIGDIR = CONFIGTESTDATA + "/streams"
SCHEMACONFIGDIR = CONFIGTESTDATA + "/schemas"
XTRCTRCONFIGDIR = CONFIGTESTDATA + "/extractors"

def create_bad_sample_template_config_dir_not_file(base_dir: Path, name: str) -> Path:
    """Function:create_bad_sample_template_config_dir_not_file"""
    config_dir = base_dir / name
    config_dir.mkdir()
    another_dir = config_dir / "config"
    another_dir.mkdir()
    return config_dir

def create_bad_sample_template_config_dir_bad_xtn(base_dir: Path, name: str) -> Path:
    """Function:create_bad_sample_template_config_dir_bad_xtn"""
    config_dir = base_dir / name
    config_dir.mkdir()
    input_content = "not json"
    file_path = config_dir / "config_0.txt"
    file_path.write_text(input_content)
    return config_dir

def test_verify_dirs_files_json_verbose_pass(capsys) -> None:
    """Function:test_verify_dirs_files_json_verbose_pass"""
    list_config_dirs=[HOSTTEMPLATEDIR,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,
        INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR]
    return_val = verify_dirs_files_json(BOOL_VERBOSE_TRUE,list_config_dirs)
    expected_output = validating_outs(HOSTTEMPLATEDIR,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,INPUTCONFIGDIR,
        STREAMCONFIGDIR,SCHEMACONFIGDIR)
    captured = capsys.readouterr()
    assert captured.out == expected_output
    assert return_val == 7

def test_verify_dirs_files_json_fail_notdir(tmp_path,capsys) -> None:
    """Function:test_verify_dirs_files_json_fail_notdir"""
    bad_path = tmp_path.as_posix()+"/config-0/config_0.json"
    list_config_dirs=[bad_path,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,
        INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR]
    with pytest.raises(SystemExit) as e:
        verify_dirs_files_json(BOOL_VERBOSE_TRUE,list_config_dirs)
    captured = capsys.readouterr()
    expected_output = (
        f"Validating data directory:{bad_path}\n"
        f"[ERROR] {bad_path} Doesn't exist, or not a dir.\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_dirs_files_json_fail_notfile(tmp_path,capsys) -> None:
    """Function:test_verify_dirs_files_json_fail_notfile"""
    hosttemplate=create_bad_sample_template_config_dir_not_file(tmp_path,"config-0")
    bad_file = tmp_path.as_posix()+"/config-0/config"
    list_config_dirs=[hosttemplate,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,
        INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR]
    with pytest.raises(SystemExit) as e:
        verify_dirs_files_json(BOOL_VERBOSE_TRUE,list_config_dirs)
    captured = capsys.readouterr()
    expected_output = (
        f"Validating data directory:{hosttemplate}\n"
        f"  Validating file:{bad_file}\n"
        f"[ERROR] {bad_file} is not a valid file.\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_dirs_files_json_fail_notjsonfile(tmp_path,capsys) -> None:
    """Function:test_verify_dirs_files_json_fail_notjsonfile"""
    hosttemplate=create_bad_sample_template_config_dir_bad_xtn(tmp_path,"config-0")
    bad_json = tmp_path.as_posix()+"/config-0/config_0.txt"
    list_config_dirs=[hosttemplate,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,
        INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR]
    with pytest.raises(SystemExit) as e:
        verify_dirs_files_json(BOOL_VERBOSE_TRUE,list_config_dirs)
    captured = capsys.readouterr()
    expected_output = (
        f"Validating data directory:{hosttemplate}\n"
        f"  Validating file:{bad_json}\n"
        f"[ERROR] {bad_json} no .json extension.\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_dirs_files_json_fail_no_json(capsys) -> None:
    """Function:test_verify_dirs_files_json_fail_no_json"""
    list_config_dirs=[HOSTTEMPLATEDIRJSON,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,
        INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR]
    with pytest.raises(SystemExit) as e:
        verify_dirs_files_json(BOOL_VERBOSE_TRUE,list_config_dirs)
    captured = capsys.readouterr()
    expected_output = (
        f"Validating data directory:{HOSTTEMPLATEDIRJSON}\n"
        f"  Validating file:{HOSTTEMPLATEFILEJSON}\n"
        f"[ERROR] {HOSTTEMPLATEFILEJSON} failed json decode.\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
