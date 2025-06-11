"""tests.helpers test_isjsonvalid module"""
from src.helpers import is_json_valid

def test_isjsonvalid_pass_host_template() -> None:
    """tests.helpers.test_isjsonvalid_pass_host_template function"""
    args = "../host-config-templates/host-template.json"
    result = is_json_valid(args)
    assert result is True

def test_isjsonvalid_fail_nonexist_file() -> None:
    """tests.helpers.test_isjsonvalid_fail_nonexist_file function"""
    args = "non_exist_file"
    result = is_json_valid(args)
    assert result is False

def test_isjsonvalid_fail_file_notjson() -> None:
    """tests.helpers.test_isjsonvalid_fail_file_notjson function"""
    args = "__init__.py"
    result = is_json_valid(args)
    assert result is False
