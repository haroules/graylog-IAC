"""tests.verify test_verify_dirs_files_json module"""
import pytest

from src.verify import verify_dirs_files_json
from tests.common.test_common import shared_asserts
from tests.setup.test_setup_common import create_bad_config_dir
from tests.verify.test_verify_common import mocked_config_tmppaths
from tests.verify.test_verify_common import validating_outs
from tests.verify.test_verify_common import create_sample_template_config_dir
from tests.verify.test_verify_common import create_sample_schema_config_dir
from tests.verify.test_verify_common import create_bad_sample_template_config_dir_not_file
from tests.verify.test_verify_common import create_bad_sample_template_config_dir_bad_xtn

MOCK_BOOL_VERBOSE = True

def test_verify_dirs_files_json_verbose_pass(tmp_path,capsys) -> None:
    """tests.verify.test_verify_dirs_files_json_verbose_pass function"""
    hosttemplatedir=create_sample_template_config_dir(tmp_path,"config-0")
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    list_config_dirs=[hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    return_val = verify_dirs_files_json(MOCK_BOOL_VERBOSE,list_config_dirs)
    expected_output = validating_outs(hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,
                        streamconfigdir,schemaconfigdir)
    captured = capsys.readouterr()
    assert captured.out == expected_output
    assert return_val == 8

def test_verify_dirs_files_json_fail_notdir(tmp_path,capsys) -> None:
    """tests.verify.test_verify_dirs_files_json_fail_notdir function"""
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    create_sample_template_config_dir(tmp_path,"config-0")
    bad_path = tmp_path.as_posix()+"/config-0/config_0.json"
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    list_config_dirs=[bad_path,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    with pytest.raises(SystemExit) as e:
        verify_dirs_files_json(MOCK_BOOL_VERBOSE,list_config_dirs)
    captured = capsys.readouterr()
    expected_output = (
        f"Validating data directory:{bad_path}\n"
        f"[ERROR] {bad_path} Doesn't exist, or not a dir.\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_dirs_files_json_fail_notfile(tmp_path,capsys) -> None:
    """tests.verify.test_verify_dirs_files_json_fail_notfile function"""
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_bad_sample_template_config_dir_not_file(tmp_path,"config-0")
    bad_file = tmp_path.as_posix()+"/config-0/config"
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    list_config_dirs=[hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    with pytest.raises(SystemExit) as e:
        verify_dirs_files_json(MOCK_BOOL_VERBOSE,list_config_dirs)
    captured = capsys.readouterr()
    expected_output = (
        f"Validating data directory:{hosttemplatedir}\n"
        f"  Validating file:{bad_file}\n"
        f"[ERROR] {bad_file} is not a valid file.\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_dirs_files_json_fail_notjsonfile(tmp_path,capsys) -> None:
    """tests.verify.test_verify_dirs_files_json_fail_notjsonfile function"""
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_bad_sample_template_config_dir_bad_xtn(tmp_path,"config-0")
    bad_json = tmp_path.as_posix()+"/config-0/config_0.txt"
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    list_config_dirs=[hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    with pytest.raises(SystemExit) as e:
        verify_dirs_files_json(MOCK_BOOL_VERBOSE,list_config_dirs)
    captured = capsys.readouterr()
    expected_output = (
        f"Validating data directory:{hosttemplatedir}\n"
        f"  Validating file:{bad_json}\n"
        f"[ERROR] {bad_json} no .json extension.\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_dirs_files_json_fail_no_json(tmp_path,capsys) -> None:
    """tests.verify.test_verify_dirs_files_json_fail_no_json function"""
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_bad_config_dir(tmp_path,"config-0")
    bad_content = tmp_path.as_posix()+"/config-0/config_1.json"
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    list_config_dirs=[hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    with pytest.raises(SystemExit) as e:
        verify_dirs_files_json(MOCK_BOOL_VERBOSE,list_config_dirs)
    captured = capsys.readouterr()
    expected_output = (
        f"Validating data directory:{hosttemplatedir}\n"
        f"  Validating file:{bad_content}\n"
        f"[ERROR] {bad_content} failed json decode.\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
