"""Module:test_graylog_clean_main"""
from unittest.mock import patch
from unittest import mock
import pytest
import graylog_clean
from tests.common.test_common import MOCK_TEST_URL
from tests.common.test_common import MOCK_TOKEN

args = ["graylog_clean.py", MOCK_TOKEN, MOCK_TEST_URL]

def test_graylog_clean_init() -> None:
    """Function:test_graylog_clean_init"""
    with patch.object(graylog_clean,"main", return_value=33):
        with patch.object(graylog_clean, "__name__", "__main__"):
            with patch.object(graylog_clean, "do_init", return_value=args):
                with patch.object(graylog_clean.sys,'exit') as mock_exit:
                    graylog_clean.init()
                    assert mock_exit.call_args[0][0] == 33

@mock.patch('graylog_clean.remove_indexsets')
@mock.patch('graylog_clean.remove_inputs')
@mock.patch('graylog_clean.remove_streams')
@mock.patch('graylog_clean.do_init')
def test_graylog_clean_main_pass(
    mock_do_init, mock_remove_streams, mock_remove_inputs, mock_remove_indexsets
) -> None:
    """Function:test_graylog_clean_main_pass"""
    mock_do_init.return_value = {"arg1": "value1"}
    mock_remove_streams.return_value = True
    mock_remove_inputs.return_value = True
    mock_remove_indexsets.return_value = True
    with mock.patch('sys.argv', ["graylog_clean.py"]):
        graylog_clean.main()
    mock_do_init.assert_called_once()
    mock_remove_streams.assert_called_once()
    mock_remove_inputs.assert_called_once()
    mock_remove_indexsets.assert_called_once()

@mock.patch('graylog_clean.do_init')
@mock.patch('graylog_clean.remove_streams')
def test_graylog_clean_main_remove_streams_fail(mock_remove_streams, mock_do_init) -> None:
    """Function:test_graylog_clean_main_remove_streams_fail"""
    mock_do_init.return_value = {"arg1": "value1"}
    mock_remove_streams.return_value = False
    with mock.patch('sys.argv', ["graylog_clean.py"]),pytest.raises(SystemExit) as e:
        graylog_clean.main()
    assert e.value.code == 1

@mock.patch('graylog_clean.do_init')
@mock.patch('graylog_clean.remove_streams')
@mock.patch('graylog_clean.remove_inputs')
def test_graylog_clean_main_remove_inputs_fail(mock_remove_inputs,mock_remove_streams,mock_do_init) -> None:
    """Function:test_graylog_clean_main_remove_inputs_fail"""
    mock_do_init.return_value = {"arg1": "value1"}
    mock_remove_streams.return_value = True
    mock_remove_inputs.return_value = False
    with mock.patch('sys.argv', ["graylog_clean.py"]),pytest.raises(SystemExit) as e:
        graylog_clean.main()
    assert e.value.code == 1

@mock.patch('graylog_clean.do_init')
@mock.patch('graylog_clean.remove_streams')
@mock.patch('graylog_clean.remove_inputs')
@mock.patch('graylog_clean.remove_indexsets')
def test_graylog_clean_main_remove_indexsets_fail(mock_remove_indexsets,mock_remove_inputs,
    mock_remove_streams, mock_do_init) -> None:
    """Function:test_graylog_clean_main_remove_indexsets_fail"""
    mock_do_init.return_value = {"arg1": "value1"}
    mock_remove_streams.return_value = True
    mock_remove_inputs.return_value = True
    mock_remove_indexsets.return_value = False
    with mock.patch('sys.argv', ["graylog_clean.py"]),pytest.raises(SystemExit) as e:
        graylog_clean.main()
    assert e.value.code == 1
