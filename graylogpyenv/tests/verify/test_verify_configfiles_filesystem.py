"""Module:tests.verify.test_verify_configfiles_filesystem"""
import os
import pytest

from src.verify import verify_configfiles_filesystem
from tests.common.test_common import static_outs
from tests.common.test_common import validating_outs
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
CONFIGTESTDATA = CWD + "/tests/test-configs"
HOSTCONFIGDIR= CONFIGTESTDATA + "/host-config"
HOSTCONFIGFILE= HOSTCONFIGDIR + "/samplehost.json"
HOSTTEMPLATEDIR = CONFIGTESTDATA + "/hosttemplate"
INDEXCONFIGDIR = CONFIGTESTDATA + "/indices"
INPUTCONFIGDIR = CONFIGTESTDATA + "/inputs"
STREAMCONFIGDIR = CONFIGTESTDATA + "/streams"
SCHEMACONFIGDIR = CONFIGTESTDATA + "/schemas"
BADSCHEMACONFIGDIR = CONFIGTESTDATA + "/badschemaswritable"
XTRCTRCONFIGDIR = CONFIGTESTDATA + "/extractors"
LIST_CONFIG_DIRS=[HOSTTEMPLATEDIR,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,
    INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR]

def test_verify_configfiles_filesystem_pass(capsys) -> None:
    """Function:test_verify_configfiles_filesystem_pass"""
    verify_configfiles_filesystem([BOOL_VERBOSE_TRUE,LIST_CONFIG_DIRS,HOSTCONFIGDIR,HOSTTEMPLATEDIR,XTRCTRCONFIGDIR,
        INDEXCONFIGDIR,INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR])
    captured = capsys.readouterr()
    value1 = static_outs()
    value2 = validating_outs(HOSTTEMPLATEDIR,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,INPUTCONFIGDIR,
                STREAMCONFIGDIR,SCHEMACONFIGDIR)
    expected_output = "Verifying config files, schema, and data directories\n" \
        + value1 + value2 + "[Done] Verifying config files, schema, and data directories\n\n"
    assert captured.out == expected_output

def test_verify_configfiles_filesystem_fail_count(mocker,capsys) -> None:
    """Function:test_verify_configfiles_filesystem_fail_count"""
    mocker.patch('src.verify.get_config_counts', return_value=8)
    with pytest.raises(SystemExit) as e:
        verify_configfiles_filesystem([BOOL_VERBOSE_TRUE,LIST_CONFIG_DIRS,HOSTCONFIGDIR,HOSTTEMPLATEDIR,XTRCTRCONFIGDIR,
            INDEXCONFIGDIR,INPUTCONFIGDIR,STREAMCONFIGDIR,SCHEMACONFIGDIR])
    captured = capsys.readouterr()
    value = validating_outs(HOSTTEMPLATEDIR,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,INPUTCONFIGDIR,
                STREAMCONFIGDIR,SCHEMACONFIGDIR)
    expected_output = (
        "Verifying config files, schema, and data directories\n"
    ) + value + "[ERROR] Config, schema files counted didn't match verified\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_configfiles_filesystem_fail_writable(capsys) -> None:
    """Function:test_verify_configfiles_filesystem_fail_writable"""
    list_config_dirs=[HOSTTEMPLATEDIR,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,
                      INPUTCONFIGDIR,STREAMCONFIGDIR,BADSCHEMACONFIGDIR]
    with pytest.raises(SystemExit) as e:
        verify_configfiles_filesystem([BOOL_VERBOSE_TRUE,list_config_dirs,HOSTCONFIGDIR,HOSTTEMPLATEDIR,XTRCTRCONFIGDIR,
            INDEXCONFIGDIR,INPUTCONFIGDIR,STREAMCONFIGDIR,BADSCHEMACONFIGDIR])
    value1 = static_outs()
    value2 = (
        f"Validating data directory:{HOSTTEMPLATEDIR}\n"
        f"  Validating file:{HOSTTEMPLATEDIR}/samplehost.json\n"
        f"Validating data directory:{HOSTCONFIGDIR}\n"
        f"  Validating file:{HOSTCONFIGDIR}/samplehost.json\n"
        f"Validating data directory:{XTRCTRCONFIGDIR}\n"
        f"  Validating file:{XTRCTRCONFIGDIR}/xtrctr_samplehost.json\n"
        f"Validating data directory:{INDEXCONFIGDIR}\n"
        f"  Validating file:{INDEXCONFIGDIR}/index_samplehost.json\n"
        f"Validating data directory:{INPUTCONFIGDIR}\n"
        f"  Validating file:{INPUTCONFIGDIR}/input_samplehost.json\n"
        f"Validating data directory:{STREAMCONFIGDIR}\n"
        f"  Validating file:{STREAMCONFIGDIR}/stream_samplehost.json\n"
        f"Validating data directory:{BADSCHEMACONFIGDIR}\n"
        f"  Validating file:{BADSCHEMACONFIGDIR}/sample_object_writable.json\n"
    )
    captured = capsys.readouterr()
    expected_output = "Verifying config files, schema, and data directories\n" + \
        value1 + value2 + f"[ERROR] {BADSCHEMACONFIGDIR}/sample_object_writable.json is writable.\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_configfiles_filesystem_fail_oserror(mocker,capsys) -> None:
    """Function:test_verify_configfiles_filesystem_fail_oserror"""
    mocker.patch('src.verify.get_config_counts', return_value=7)
    with pytest.raises(SystemExit) as e:
        verify_configfiles_filesystem([BOOL_VERBOSE_TRUE,LIST_CONFIG_DIRS,HOSTCONFIGDIR,HOSTTEMPLATEDIR,XTRCTRCONFIGDIR,
            INDEXCONFIGDIR,INPUTCONFIGDIR,STREAMCONFIGDIR,"bad_path"])
    value = validating_outs(HOSTTEMPLATEDIR,HOSTCONFIGDIR,XTRCTRCONFIGDIR,INDEXCONFIGDIR,INPUTCONFIGDIR,
                STREAMCONFIGDIR,SCHEMACONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        "Verifying config files, schema, and data directories\n"
    ) + value + "[ERROR] An OSError occurred in verify_configfiles_filesystem: [Errno 2] No such file or directory: 'bad_path'\n"
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
