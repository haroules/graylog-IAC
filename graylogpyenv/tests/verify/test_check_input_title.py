"""Module:tests.verify.test_check_input_title"""
import os
import json
import pytest

from src.verify import check_input_title
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"
with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
    dict_config = json.load(file)

def test_check_input_title_pass(capsys) -> None:
    """Function:test_check_input_title_pass"""
    check_input_title(BOOL_VERBOSE_TRUE,"samplehost",dict_config)
    captured = capsys.readouterr()
    expected_output = (
        "    Checking input title\n"
    )
    assert captured.out == expected_output

def test_check_input_title_fail(capsys) -> None:
    """Function:test_check_input_title_fail"""
    with pytest.raises(SystemExit) as e:
        check_input_title(BOOL_VERBOSE_TRUE,"wronghost",dict_config)
    captured = capsys.readouterr()
    expected_output = (
        "    Checking input title\n"
        "[ERROR] wronghost not found in object file name or object title input_samplehost.json\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
