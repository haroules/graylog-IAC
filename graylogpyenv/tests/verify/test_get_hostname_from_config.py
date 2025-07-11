"""Module:tests.verify.test_get_hostname_from_config"""
import os
import json

from src.verify import get_hostname_from_config
from tests.common.test_common import BOOL_VERBOSE_TRUE

CWD = os.getcwd()
HOSTCONFIGDIR= CWD + "/tests/test-configs/host-config"
HOSTCONFIGFILE= CWD + "/tests/test-configs/host-config/samplehost.json"
with open(HOSTCONFIGFILE, "r", encoding="utf-8") as file:
    dict_config = json.load(file)

def test_get_hostname_from_config_pass(capsys) -> None:
    """Function:test_get_hostname_from_config_pass"""
    get_hostname_from_config(BOOL_VERBOSE_TRUE,HOSTCONFIGFILE,dict_config)
    captured = capsys.readouterr()
    expected_output = (
        f"  Checking host config: {HOSTCONFIGDIR}/samplehost.json contains: samplehost\n"
    )
    assert captured.out == expected_output
