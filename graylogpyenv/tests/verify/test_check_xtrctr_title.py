"""Module:tests.verify.test_check_xtrctr_title"""
import os
import json
import pytest
from src.verify import check_xtrctr_title
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"
HOSTCONFIGFILENOXTRCTR = CWD + "/tests/test-configs/host-config-noxtrctr/samplehost.json"

def test_check_xtrctr_title_pass(capsys) -> None:
    """Function:test_check_xtrctr_title_pass"""
    with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    check_xtrctr_title(BOOL_VERBOSE_TRUE,HOSTCONFIGFILE,"samplehost",dict_config)
    captured = capsys.readouterr()
    expected_output = (
        "    Checking extractor title(s)\n"
    )
    assert captured.out == expected_output

def test_check_no_xtrctr_title_pass(capsys) -> None:
    """Function:test_check_no_xtrctr_title_pass"""
    with open(HOSTCONFIGFILENOXTRCTR, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    check_xtrctr_title(BOOL_VERBOSE_TRUE,HOSTCONFIGFILE,"samplehost",dict_config)
    captured = capsys.readouterr()
    expected_output = (
        f"    Config set has no extractors defined: {HOSTCONFIGFILE}\n"
    )
    assert captured.out == expected_output

def test_check_xtrctr_title_fail(capsys) -> None:
    """Function:test_check_xtrctr_title_fail"""
    with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    with pytest.raises(SystemExit) as e:
        check_xtrctr_title(BOOL_VERBOSE_TRUE,HOSTCONFIGFILE,"wronghost",dict_config)
    captured = capsys.readouterr()
    expected_output = (
        "    Checking extractor title(s)\n"
        "[ERROR] wronghost not found in extractor file name xtrctr_samplehost.json\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
