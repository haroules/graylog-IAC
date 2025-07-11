"""Module:tests.verify.test_check_stream_title"""
import os
import json
import pytest
from src.verify import check_stream_title
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
CONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"

def test_check_stream_title_pass(capsys) -> None:
    """Function:test_check_stream_title_pass"""
    with open(CONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    check_stream_title(BOOL_VERBOSE_TRUE,"samplehost",dict_config)
    captured = capsys.readouterr()
    expected_output = (
        "    Checking stream title\n"
    )
    assert captured.out == expected_output

def test_check_stream_title_fail(capsys) -> None:
    """Function:test_check_stream_title_fail"""
    with open(CONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    with pytest.raises(SystemExit) as e:
        check_stream_title(BOOL_VERBOSE_TRUE,"wronghost",dict_config)
    captured = capsys.readouterr()
    expected_output = (
        "    Checking stream title\n"
        "[ERROR] wronghost not found in object filename or title stream_samplehost.json\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
