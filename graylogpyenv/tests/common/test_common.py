"""Module:tests.common.test_common"""
import json
from pathlib import Path
from unittest.mock import Mock

BOOL_VERBOSE_TRUE = True
BOOL_VERBOSE_FALSE = False
MOCK_TOKEN = "A1B2C3D4E5F6G7H8I9J1K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z"
MOCK_SCRIPT = "graylog_setup.py"
MOCK_DICT_GET_HEADERS = {"Authorization": "Basic SampleToken",
                         "Content-Type": "application/json"}
MOCK_DICT_POST_HEADERS = {"Authorization": "Basic SampleToken",
                        "Content-Type": "application/json",
                        "X-Requested-By": "XMLHttpRequest"}
MOCK_TEST_URL = "http://localhost.local"
MOCK_STR_STREAMS_URL = "http://localhost.local/streams"
MOCK_STR_INDEXSETS_URL = "http://localhost.local/index_sets"
MOCK_STR_INPUTS_URL = "http://localhost.local/inputs"
MOCK_STR_NODE_URL = "http://localhost.local/nodeidurl"
MOCK_HOST_DATA=[{
        "index_config_file":"index_samplehost.json",
        "index_title":"samplehost-default-index",
        "input_config_file":"input_samplehost.json",
        "input_title":"samplehost-input",
        "extractors_total":1,
        "extractors":[{
            "extractor_config_file" :"xtrctr_samplehost.json",
            "extractor_title" : "samplehost_extractor"
        }],
        "stream_config_file":"stream_samplehost.json",
        "stream_title":"samplehost-stream"
        }]

def static_outs() -> str:
    """Function:static_outs"""
    return(
        "7 Data Dirs\n"
        "1 Schema files\n"
        "1 Host cfg files\n"
        "1 Host cfg templates\n"
        "1 Index config files\n"
        "1 Input config files\n"
        "1 Stream config files\n"
        "1 Extractor config files\n\n"
    )

def validating_outs(hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
    inputsconfigdir,streamconfigdir,schemaconfigdir):
    """Function:validating_outs"""
    return(
        f"Validating data directory:{hosttemplatedir}\n"
        f"  Validating file:{hosttemplatedir}/samplehost.json\n"
        f"Validating data directory:{hostconfigdir}\n"
        f"  Validating file:{hostconfigdir}/samplehost.json\n"
        f"Validating data directory:{extrctrconfigdir}\n"
        f"  Validating file:{extrctrconfigdir}/xtrctr_samplehost.json\n"
        f"Validating data directory:{indexconfigdir}\n"
        f"  Validating file:{indexconfigdir}/index_samplehost.json\n"
        f"Validating data directory:{inputsconfigdir}\n"
        f"  Validating file:{inputsconfigdir}/input_samplehost.json\n"
        f"Validating data directory:{streamconfigdir}\n"
        f"  Validating file:{streamconfigdir}/stream_samplehost.json\n"
        f"Validating data directory:{schemaconfigdir}\n"
        f"  Validating file:{schemaconfigdir}/sample_object_schema.json\n"
    )

def mock_get_response(status_code: int, text :str) -> Mock:
    """Function:mock_get_response"""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_response.text = text
    mock_response.raise_for_status = Mock()
    return mock_response

def shared_asserts(capturedout,expectedout,evaluecode,etype) -> None:
    """Function:shared_asserts"""
    assert capturedout == expectedout
    assert evaluecode == 1
    assert etype == SystemExit

def folder_asserts(backup_base :Path) -> None:
    """Function:folder_asserts"""
    assert backup_base.exists()
    assert backup_base.is_dir()
    configa = backup_base / "configA"
    configb = backup_base / "configB"
    assert configa.exists()
    assert configb.exists()
    for i in range(2):
        assert (configa / f"config_{i}.json").read_text() == f"some not json text {i}"
        assert (configb / f"config_{i}.json").read_text() == f"some not json text {i}"

def create_empty_config_dir(base_dir: Path, name: str) -> Path:
    """Function:create_empty_config_dir"""
    config_dir = base_dir / name
    config_dir.mkdir()
    return config_dir

def create_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    """Function:create_config_dir"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        file_path.write_text(f"some not json text {i}")
    return config_dir

def create_stream_config_dir(indexsetid :str, base_dir: Path, name: str) -> Path:
    """Function:create_stream_config_dir"""
    config_dir = base_dir / name
    config_dir.mkdir()
    file_path = config_dir / "stream_samplehost.json"
    input_json_content = {
        f"{indexsetid}": "samplehost_index_setid",
        "title": "samplehost-stream",
        "rules": [{
            "field": "input",
            "description": "",
            "type": 1,
            "inverted": False,
            "value": "bad_title"
        }]
    }
    file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_badcount_host_config_dir(base_dir: Path, name: str) -> Path:
    """Function:create_badcount_host_config_dir"""
    config_dir = base_dir / name
    config_dir.mkdir()
    file_path = config_dir / "config_0.json"
    input_json_content = {"hostname":"samplehost",
        "config_sets_total":2,
        "config_sets": MOCK_HOST_DATA
        }
    file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_badjson_host_config_dir(base_dir: Path, name: str) -> Path:
    """Function:create_badjson_host_config_dir"""
    config_dir = base_dir / name
    config_dir.mkdir()
    file_path = config_dir / "config_0.json"
    input_json_content = "some text"
    file_path.write_text(input_json_content)
    return config_dir
