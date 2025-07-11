"""Module:tests.verify.test_get_config_counts"""
import os
import pytest

from src.verify import get_config_counts
from tests.common.test_common import static_outs
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
XTRCTRCONFIGDIR = CWD + "/tests/test-configs/extractors"
HOSTCONFIGDIR = CWD + "/tests/test-configs/host-config"
INDEXCONFIGDIR = CWD + "/tests/test-configs/indices"
INPUTCONFIGDIR = CWD + "/tests/test-configs/inputs"
STREAMCONFIGDIR = CWD + "/tests/test-configs/streams"
SCHEMACONFIGDIR = CWD + "/tests/test-configs/schemas"
HOSTTEMPLATEDIR = CWD + "/tests/test-configs/hosttemplate"

def test_get_config_counts_verbose_pass(capsys) -> None:
    """Function:test_get_config_counts_verbose_pass"""
    return_val = get_config_counts(BOOL_VERBOSE_TRUE,[HOSTCONFIGDIR,HOSTTEMPLATEDIR,
                    XTRCTRCONFIGDIR,INDEXCONFIGDIR,INPUTCONFIGDIR,STREAMCONFIGDIR,
                    SCHEMACONFIGDIR],HOSTCONFIGDIR,HOSTTEMPLATEDIR,XTRCTRCONFIGDIR,
                    INDEXCONFIGDIR,INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR)
    captured = capsys.readouterr()
    expected_output = static_outs()
    assert captured.out == expected_output
    assert return_val == 7

def test_get_config_counts_fail_oserror(capsys) -> None:
    """Function:test_get_config_counts_fail_oserror"""
    with pytest.raises(SystemExit) as e:
        get_config_counts(BOOL_VERBOSE_TRUE,[HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,
            STREAMCONFIGDIR,SCHEMACONFIGDIR],"bad_path",HOSTTEMPLATEDIR,XTRCTRCONFIGDIR,
            INDEXCONFIGDIR,INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR)
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in get_config_counts:"
    expected_output = (
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
