"""Module:tests.verify.test_check_hostconfig_objects_unique"""
import os
import json
import pytest

from src.verify import check_hostconfig_indexes_unique
from src.verify import check_hostconfig_streams_unique
from src.verify import check_hostconfig_xtrctrs_unique
from tests.common.test_common import shared_asserts
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
HOSTCONFIGDIR = CWD + "/tests/test-configs/host-config"
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"
BADHOSTCONFIGFILE = CWD + "/tests/test-configs/bad-host-config/samplehost.json"

def test_check_hostconfig_indexes_unique_pass(capsys) -> None:
    """Function:test_check_hostconfig_indexes_unique_pass"""
    with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    check_hostconfig_indexes_unique(BOOL_VERBOSE_TRUE,1,dict_config,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        f"    1 Unique indexes defined in: {HOSTCONFIGDIR}\n"
    )
    assert captured.out == expected_output

def test_check_hostconfig_streams_unique_pass(capsys) -> None:
    """Function:test_check_hostconfig_streams_unique_pass"""
    with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    check_hostconfig_streams_unique(BOOL_VERBOSE_TRUE,1,dict_config,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        f"    1 Unique streams defined in: {HOSTCONFIGDIR}\n"
    )
    assert captured.out == expected_output

def test_check_hostconfig_xtrctrs_unique_pass(capsys) -> None:
    """Function:test_check_hostconfig_xtrctrs_unique_pass"""
    with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    check_hostconfig_xtrctrs_unique(BOOL_VERBOSE_TRUE,dict_config,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        f"    1 Unique extractors defined in: {HOSTCONFIGDIR}\n"
    )
    assert captured.out == expected_output

def test_check_hostconfig_indexes_unique_fail(capsys) -> None:
    """Function:test_check_hostconfig_indexes_unique_fail"""
    with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    with pytest.raises(SystemExit) as e:
        check_hostconfig_indexes_unique(BOOL_VERBOSE_TRUE,2,dict_config,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        f"[ERROR] Duplicate indexes in host config file:{HOSTCONFIGDIR}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_check_hostconfig_streams_unique_fail(capsys) -> None:
    """Function:test_check_hostconfig_streams_unique_fail"""
    with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    with pytest.raises(SystemExit) as e:
        check_hostconfig_streams_unique(BOOL_VERBOSE_TRUE,2,dict_config,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        f"[ERROR] Duplicate streams in host config file: {HOSTCONFIGDIR}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)

def test_check_hostconfig_xtrctrs_unique_fail(capsys) -> None:
    """Function:test_check_hostconfig_xtrctrs_unique_fail"""
    with open(BADHOSTCONFIGFILE, "r", encoding="utf-8") as file:
        dict_config = json.load(file)
    with pytest.raises(SystemExit) as e:
        check_hostconfig_xtrctrs_unique(BOOL_VERBOSE_TRUE,dict_config,HOSTCONFIGDIR)
    captured = capsys.readouterr()
    expected_output = (
        f"[ERROR] Defined extractors != parsed extractors in host file {HOSTCONFIGDIR}\n"
    )
    shared_asserts(captured.out,expected_output,e.value.code,e.type)
