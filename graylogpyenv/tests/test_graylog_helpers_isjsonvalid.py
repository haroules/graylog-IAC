import pytest
from src.graylog_helpers import is_json_valid

def test_isjsonvalid_pass_host_template():
    args = "../host-config-templates/host-template.json"
    result = is_json_valid(args)
    assert result == True

def test_isjsonvalid_fail_file_non_exist(capsys):
    args = "badfilepath"
    result = is_json_valid(args)
    captured = capsys.readouterr()
    assert captured.out == f"[ERROR] File doesn't exist {args}\n" 
    assert result == False

def test_isjsonvalid_fail_file_notjson(capsys):
    args = "__init__.py"    
    result = is_json_valid(args)
    captured = capsys.readouterr()
    assert f"[ERROR] There was a problem decoding json: {args}\n" == captured.out
    assert result == False
