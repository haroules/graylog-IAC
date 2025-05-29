import pytest
from src.graylog_helpers import contains_sublist

def test_contains_sublist_pass_valid_list():
    sub_list = ["item one", "item two"]
    main_list = ["item three", "item one", "item two"]
    result = contains_sublist(sub_list,main_list)
    assert result == True

def test_contains_sublist_fail_invalid_item(capsys):
    with pytest.raises(SystemExit) as e:
        sub_list = "item one"
        main_list = ["item three", "item one", "item two"]
        contains_sublist(sub_list,main_list)
    captured = capsys.readouterr()
    assert captured.out == "[ERROR] One or more items passed to contains_sublist is not a list\n"
    assert e.value.code == 1

def test_contains_sublist_fail_sublist_notinlist():
    sub_list = ["item four"]
    main_list = ["item three", "item one", "item two"]
    result = contains_sublist(sub_list,main_list)
    assert result == False    
        