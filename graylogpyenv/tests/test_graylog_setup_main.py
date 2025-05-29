"""
graylog test_graylog_setup_main module
"""
from unittest.mock import patch
from unittest import mock
import graylog_setup


VALID_SCRIPT = "graylog_clean.py"
# A valid 52-char alphanumeric token
VALID_TOKEN = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6"
VALID_URL = "http://graylogsetup.example.com"
EXPECTED_VALID_OUTPUT = (
    "Checking arguments and validating the inputs.\n"
    "[Done] Checking arguments and validating the inputs.\n\n"
)
args = [VALID_SCRIPT, VALID_TOKEN, VALID_URL]


def test_graylog_setup_main():
    """Function test_graylog_setup_main"""
    with patch.object(graylog_setup,"main", return_value=None):
        with patch.object(graylog_setup, "__name__", "__main__"):
            with patch.object(graylog_setup, "do_init", return_value=args):
                with patch.object(graylog_setup.sys,'exit') as mock_exit:
                    graylog_setup.init()
                    assert mock_exit.call_args[0][0] is None

@mock.patch('graylog_setup.create_streams')
@mock.patch('graylog_setup.create_extractors')
@mock.patch('graylog_setup.create_static_fields')
@mock.patch('graylog_setup.create_inputs')
@mock.patch('graylog_setup.create_indices')
@mock.patch('graylog_setup.make_config_backup')
@mock.patch('graylog_setup.do_init')
def test_graylog_setup_main_success(
    mock_do_init, mock_make_config_backup, mock_create_indices,
    mock_create_inputs, mock_create_static_fields,
    mock_create_extractors, mock_create_streams
):
    """Function test_graylog_setup_main_success"""
    mock_do_init.return_value = {"arg1": "value1"}
    mock_make_config_backup.return_value = True
    mock_create_indices.return_value = None
    mock_create_inputs.return_value = None
    mock_create_static_fields.return_value = None
    mock_create_extractors.return_value = None
    mock_create_streams.return_value = None

    with mock.patch('sys.argv', ["graylog_setup.py"]):
        graylog_setup.main()
    mock_do_init.assert_called_once()
    mock_make_config_backup.assert_called_once()
    mock_create_indices.assert_called_once()
    mock_create_inputs.assert_called_once()
    mock_create_static_fields.assert_called_once()
    mock_create_extractors.assert_called_once()
    mock_create_streams.assert_called_once()
