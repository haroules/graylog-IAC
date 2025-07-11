"""Module:tests.verify.test_verify_hostconfigfiles_deps_schema"""
import os
import pytest
from src.verify import verify_hostconfigfiles_deps_schema
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE

VALID_CWD = os.path.dirname(os.getcwd())
SCHEMA_PATH = VALID_CWD + "/schemas"
TEST_PATH = VALID_CWD + "/graylogpyenv/tests/test-configs"
SCHEMA_INDEX = SCHEMA_PATH + "/index.json"
SCHEMA_INPUT = SCHEMA_PATH + "/input.json"
SCHEMA_STREAM = SCHEMA_PATH + "/stream.json"
SCHEMA_EXTRACTOR = SCHEMA_PATH + "/extractor.json"
HOSTCONFIGDIR = TEST_PATH + "/host-config"
HOSTCFGDIRNOXTR = TEST_PATH + "/host-config-noxtrctr"
HOSTCFGDRBADPTH = "bad_path"
HOSTCFGNOJSON = TEST_PATH + "/badschemasjson"
INDEXCONFIGDIR = TEST_PATH + "/indices"
INPUTSCONFIGDIR = TEST_PATH + "/inputs"
STREAMCONFIGDIR = TEST_PATH + "/streams"
XTRCTRCONFIGDIR = TEST_PATH + "/extractors"

def test_verify_hostconfigfiles_deps_schema_pass(capsys) -> None:
    """Function:test_verify_hostconfigfiles_deps_schema_pass"""
    verify_hostconfigfiles_deps_schema(BOOL_VERBOSE_TRUE,HOSTCONFIGDIR,SCHEMA_INDEX,
        INDEXCONFIGDIR,SCHEMA_INPUT,INPUTSCONFIGDIR,SCHEMA_STREAM,STREAMCONFIGDIR,
        SCHEMA_EXTRACTOR,XTRCTRCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        "Analyzing host configuration file object's schema\n"
        f"  Verifying host configuration file dependencies for: {HOSTCONFIGDIR}/samplehost.json\n"
        "    Verifying object(s): ['index_samplehost.json']\n"
        f"      Using schema: {SCHEMA_INDEX}\n"
        f"      Checking: {INDEXCONFIGDIR}/index_samplehost.json\n"
        "      Object(s) align with schema.\n"
        "    Verifying object(s): ['input_samplehost.json']\n"
        f"      Using schema: {SCHEMA_INPUT}\n"
        f"      Checking: {INPUTSCONFIGDIR}/input_samplehost.json\n"
        "      Object(s) align with schema.\n"
        "    Verifying object(s): ['stream_samplehost.json']\n"
        f"      Using schema: {SCHEMA_STREAM}\n"
        f"      Checking: {STREAMCONFIGDIR}/stream_samplehost.json\n"
        "      Object(s) align with schema.\n"
        "    Verifying object(s): ['xtrctr_samplehost.json']\n"
        f"      Using schema: {SCHEMA_EXTRACTOR}\n"
        f"      Checking: {XTRCTRCONFIGDIR}/xtrctr_samplehost.json\n"
        "      Object(s) align with schema.\n"
        "[Done] Analyzing host configuration file object's schema.\n\n"
    )
    assert expected_output == captured.out

def test_verify_hostconfigfiles_deps_schema_no_xtrctr_pass(capsys) -> None:
    """Function:test_verify_hostconfigfiles_deps_schema_no_xtrctr_pass"""
    verify_hostconfigfiles_deps_schema(BOOL_VERBOSE_TRUE,HOSTCFGDIRNOXTR,SCHEMA_INDEX,
        INDEXCONFIGDIR,SCHEMA_INPUT,INPUTSCONFIGDIR,SCHEMA_STREAM,STREAMCONFIGDIR,
        SCHEMA_EXTRACTOR,XTRCTRCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        "Analyzing host configuration file object's schema\n"
        f"  Verifying host configuration file dependencies for: {HOSTCFGDIRNOXTR}/samplehost.json\n"
        "    Verifying object(s): ['index_samplehost.json']\n"
        f"      Using schema: {SCHEMA_INDEX}\n"
        f"      Checking: {INDEXCONFIGDIR}/index_samplehost.json\n"
        "      Object(s) align with schema.\n"
        "    Verifying object(s): ['input_samplehost.json']\n"
        f"      Using schema: {SCHEMA_INPUT}\n"
        f"      Checking: {INPUTSCONFIGDIR}/input_samplehost.json\n"
        "      Object(s) align with schema.\n"
        "    Verifying object(s): ['stream_samplehost.json']\n"
        f"      Using schema: {SCHEMA_STREAM}\n"
        f"      Checking: {STREAMCONFIGDIR}/stream_samplehost.json\n"
        "      Object(s) align with schema.\n"
        f"    No extractors defined in {HOSTCFGDIRNOXTR}/samplehost.json\n"
        "[Done] Analyzing host configuration file object's schema.\n\n"
    )
    assert expected_output == captured.out

def test_verify_hostconfigfiles_deps_schema_fail_oserror(capsys) -> None:
    """Function:test_verify_hostconfigfiles_deps_schema_fail_oserror"""
    with pytest.raises(SystemExit) as e:
        verify_hostconfigfiles_deps_schema(BOOL_VERBOSE_TRUE,HOSTCFGDRBADPTH,SCHEMA_INDEX,
            INDEXCONFIGDIR,SCHEMA_INPUT,INPUTSCONFIGDIR,SCHEMA_STREAM,STREAMCONFIGDIR,
            SCHEMA_EXTRACTOR,XTRCTRCONFIGDIR)
    captured = capsys.readouterr()
    message = "[ERROR] An OSError occurred in verify_hostconfigfiles_deps_schema:"
    expected_output = (
        "Analyzing host configuration file object's schema\n"
        f"{message} [Errno 2] No such file or directory: 'bad_path'\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_verify_hostconfigfiles_deps_schema_fail_json_decode(capsys) -> None:
    """Function:test_verify_hostconfigfiles_deps_schema_fail_json_decode"""
    with pytest.raises(SystemExit) as e:
        verify_hostconfigfiles_deps_schema(BOOL_VERBOSE_TRUE,HOSTCFGNOJSON,SCHEMA_INDEX,
            INDEXCONFIGDIR,SCHEMA_INPUT,INPUTSCONFIGDIR,SCHEMA_STREAM,STREAMCONFIGDIR,
            SCHEMA_EXTRACTOR,XTRCTRCONFIGDIR)
    captured = capsys.readouterr()
    message = "[ERROR] Problem decoding json in verify_hostconfigfiles_deps_schema:"
    expected_output = (
        "Analyzing host configuration file object's schema\n"
        f"  Verifying host configuration file dependencies for: {HOSTCFGNOJSON}/sample_object_text.json\n"
        f"{message} Expecting value: line 1 column 1 (char 0)\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
