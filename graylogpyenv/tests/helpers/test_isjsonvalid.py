"""Module:tests.helpers.test_isjsonvalid"""
from src.helpers import is_json_valid

def test_isjsonvalid_pass_host_template() -> None:
    """Function:test_isjsonvalid_pass_host_template"""
    args = "../host-config-templates/host-template.json"
    result = is_json_valid(args)
    assert result is True

def test_isjsonvalid_fail_nonexist_file() -> None:
    """Function:test_isjsonvalid_fail_nonexist_file"""
    args = "non_exist_file"
    result = is_json_valid(args)
    assert result is False

def test_isjsonvalid_fail_file_notjson() -> None:
    """Function:test_isjsonvalid_fail_file_notjson"""
    args = "__init__.py"
    result = is_json_valid(args)
    assert result is False
