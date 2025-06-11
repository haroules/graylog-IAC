"""tests.verify test_get_config_counts module"""
import pytest

from src.verify import get_config_counts
from tests.common.test_common import static_outs
from tests.verify.test_verify_common import create_sample_schema_config_dir
from tests.verify.test_verify_common import create_sample_template_config_dir
from tests.verify.test_verify_common import mocked_config_tmppaths
from tests.common.test_common import shared_asserts

MOCK_BOOL_VERBOSE = True

def test_get_config_counts_verbose_pass(tmp_path,capsys) -> None:
    """tests.verify.test_get_config_counts_verbose_pass function"""
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_sample_template_config_dir(tmp_path,"config-0")
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    return_val = get_config_counts(MOCK_BOOL_VERBOSE,[hostconfigdir,hosttemplatedir,
                    extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir,
                    schemaconfigdir],hostconfigdir,hosttemplatedir,extrctrconfigdir,
                    indexconfigdir,inputsconfigdir,streamconfigdir,schemaconfigdir)
    captured = capsys.readouterr()
    expected_output = static_outs()
    assert captured.out == expected_output
    assert return_val == 8

def test_get_config_counts_fail_oserror(tmp_path,capsys) -> None:
    """tests.verify.test_get_config_counts_fail_oserror function"""
    hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir = mocked_config_tmppaths(tmp_path)
    hosttemplatedir=create_sample_template_config_dir(tmp_path,"config-0")
    schemaconfigdir=create_sample_schema_config_dir(tmp_path,"config-6")
    with pytest.raises(SystemExit) as e:
        get_config_counts(MOCK_BOOL_VERBOSE,[hostconfigdir,extrctrconfigdir,indexconfigdir,
            streamconfigdir,schemaconfigdir],"bad_path",hosttemplatedir,extrctrconfigdir,
            indexconfigdir,inputsconfigdir,streamconfigdir,schemaconfigdir)
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in get_config_counts:"
    expected_output = (
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
