"""helpers test_isjsonvalid module"""
import pytest

from src.helpers import is_json_valid

def test_isjsonvalid_pass_host_template() -> None:
    """helpers test_isjsonvalid_pass_host_template function"""
    args = "../host-config-templates/host-template.json"
    result = is_json_valid(args)
    assert result is True

def test_isjsonvalid_fail_nonexist_file() -> None:
    """helpers test_isjsonvalid_fail_nonexist_file function"""
    args = "non_exist_file"
    result = is_json_valid(args)
    assert result is False

def test_isjsonvalid_fail_file_notjson(capsys) -> None:
    """helpers test_isjsonvalid_fail_file_notjson function"""
    args = "__init__.py"
    with pytest.raises(SystemExit):
        is_json_valid(args)
    captured = capsys.readouterr()
    assert f"[ERROR] Problem decoding json in is_json_valid: {args}\n" == captured.out
