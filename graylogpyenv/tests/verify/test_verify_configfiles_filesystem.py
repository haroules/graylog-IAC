"""tests.verify test_verify_configfiles_filesystem module"""
import pytest

from src.verify import verify_configfiles_filesystem
from tests.common.test_common import static_outs
from tests.verify.test_verify_common import validating_outs
from tests.verify.test_verify_common import create_sample_schema_config_dir
from tests.verify.test_verify_common import create_sample_template_config_dir
from tests.verify.test_verify_common import create_sample_schema_config_dir_writable
from tests.verify.test_verify_common import mocked_config_tmppaths
from tests.common.test_common import shared_asserts

MOCK_BOOL_VERBOSE = True

def test_verify_configfiles_filesystem_pass(tmp_path,capsys) -> None:
    """ tests.verify.test_verify_configfiles_filesystem_pass function """
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_sample_template_config_dir(tmp_path,"config-0")
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    list_config_dirs=[hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    verify_configfiles_filesystem([MOCK_BOOL_VERBOSE,list_config_dirs,hostconfigdir,hosttemplatedir,extrctrconfigdir,
        indexconfigdir,inputsconfigdir,streamconfigdir,schemaconfigdir])
    captured = capsys.readouterr()
    value1 = static_outs()
    value2 = validating_outs(hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,
                streamconfigdir,schemaconfigdir)
    expected_output = "Verifying config files, schema, and data directories\n" \
        + value1 + value2 + "[Done] Verifying config files, schema, and data directories\n\n"
    assert captured.out == expected_output

def test_verify_configfiles_filesystem_fail_count(tmp_path,mocker,capsys) -> None:
    """ tests.verify.test_verify_configfiles_filesystem_fail_count function """
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_sample_template_config_dir(tmp_path,"config-0")
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    list_config_dirs=[hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    mocker.patch('src.verify.get_config_counts', return_value=7)
    with pytest.raises(SystemExit) as e:
        verify_configfiles_filesystem([MOCK_BOOL_VERBOSE,list_config_dirs,hostconfigdir,hosttemplatedir,extrctrconfigdir,
            indexconfigdir,inputsconfigdir,streamconfigdir,schemaconfigdir])
    captured = capsys.readouterr()
    value = validating_outs(hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,
                streamconfigdir,schemaconfigdir)
    expected_output = (
        "Verifying config files, schema, and data directories\n"
    ) + value + "[ERROR] Config, schema files counted didn't match verified\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_configfiles_filesystem_fail_writable(tmp_path,capsys) -> None:
    """ tests.verify.test_verify_configfiles_filesystem_fail_writable function """
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_sample_template_config_dir(tmp_path,"config-0")
    schemaconfigdir=create_sample_schema_config_dir_writable(tmp_path,"config-6")
    list_config_dirs=[hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    with pytest.raises(SystemExit) as e:
        verify_configfiles_filesystem([MOCK_BOOL_VERBOSE,list_config_dirs,hostconfigdir,hosttemplatedir,extrctrconfigdir,
            indexconfigdir,inputsconfigdir,streamconfigdir,schemaconfigdir])
    value1 = static_outs()
    value2 = validating_outs(hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,
                streamconfigdir,schemaconfigdir)
    captured = capsys.readouterr()
    expected_output = "Verifying config files, schema, and data directories\n" + \
        value1 + value2 + f"[ERROR] {schemaconfigdir}/config_0.json is writable.\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_configfiles_filesystem_fail_oserror(tmp_path,mocker,capsys) -> None:
    """ tests.verify.test_verify_configfiles_filesystem_fail_oserror function """
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_sample_template_config_dir(tmp_path,"config-0")
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    list_config_dirs=[hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
                      inputsconfigdir,streamconfigdir,schemaconfigdir]
    mocker.patch('src.verify.get_config_counts', return_value=8)
    with pytest.raises(SystemExit) as e:
        verify_configfiles_filesystem([MOCK_BOOL_VERBOSE,list_config_dirs,hostconfigdir,hosttemplatedir,extrctrconfigdir,
            indexconfigdir,inputsconfigdir,streamconfigdir,"bad_path"])
    value = validating_outs(hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,
                streamconfigdir,schemaconfigdir)
    captured = capsys.readouterr()
    expected_output = (
        "Verifying config files, schema, and data directories\n"
    ) + value + "[ERROR] An OSError occurred in verify_configfiles_filesystem: [Errno 2] No such file or directory: 'bad_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
