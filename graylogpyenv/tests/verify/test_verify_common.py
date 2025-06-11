"""tests.verify test_verify_common module"""
import json
from pathlib import Path
from stat import S_IREAD

from tests.common.test_common import create_sample_index_config_dir
from tests.common.test_common import create_sample_input_config_dir
from tests.common.test_common import create_sample_host_config_dir
from tests.common.test_common import create_sample_extractor_config_dir
from tests.common.test_common import create_sample_stream_config_dir
from tests.common.test_common import MOCK_HOST_DATA

def mocked_config_tmppaths(tmp_path):
    """ tests.verify.mocked_config_tmppaths function """
    hostconfigdir=create_sample_host_config_dir(tmp_path,"config-1")
    extrctrconfigdir=create_sample_extractor_config_dir(tmp_path,"config-2")
    indexconfigdir=create_sample_index_config_dir(tmp_path,"config-3")
    inputsconfigdir=create_sample_input_config_dir(tmp_path,"config-4")
    streamconfigdir=create_sample_stream_config_dir(tmp_path,"config-5")
    return hostconfigdir,extrctrconfigdir,indexconfigdir,inputsconfigdir,streamconfigdir

def validating_outs(hosttemplatedir,hostconfigdir,extrctrconfigdir,indexconfigdir,
    inputsconfigdir,streamconfigdir,schemaconfigdir):
    """ tests.verify.validating_outs function """
    return(
        f"Validating data directory:{hosttemplatedir}\n"
        f"  Validating file:{hosttemplatedir}/config_0.json\n"
        f"Validating data directory:{hostconfigdir}\n"
        f"  Validating file:{hostconfigdir}/config_0.json\n"
        f"Validating data directory:{extrctrconfigdir}\n"
        f"  Validating file:{extrctrconfigdir}/config_0.json\n"
        f"Validating data directory:{indexconfigdir}\n"
        f"  Validating file:{indexconfigdir}/config_1.json\n"
        f"  Validating file:{indexconfigdir}/config_0.json\n"
        f"Validating data directory:{inputsconfigdir}\n"
        f"  Validating file:{inputsconfigdir}/config_0.json\n"
        f"Validating data directory:{streamconfigdir}\n"
        f"  Validating file:{streamconfigdir}/config_0.json\n"
        f"Validating data directory:{schemaconfigdir}\n"
        f"  Validating file:{schemaconfigdir}/config_0.json\n"
    )

def create_sample_schema_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.verify.create_sample_schema_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = {
            "sample_object": "sample_object_id",
            "title": "samplobject-title",
        }
        file_path.write_text(json.dumps(input_json_content,indent=2))
        file_path.chmod(S_IREAD)
    return config_dir

def create_sample_schema_config_dir_writable(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.verify.create_sample_schema_config_dir_writable function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = {
            "sample_object": "sample_object_id",
            "title": "samplobject-title",
        }
        file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_sample_template_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.verify.create_sample_template_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = {
            "hostname" : "<replace>",
            "config_sets_total" : 1,
            "config_sets" : MOCK_HOST_DATA
        }
        file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_bad_sample_template_config_dir_not_file(base_dir: Path, name: str) -> Path:
    """tests.verify.create_bad_sample_template_config_dir_not_file function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    another_dir = config_dir / "config"
    another_dir.mkdir()
    return config_dir

def create_bad_sample_template_config_dir_bad_xtn(base_dir: Path, name: str) -> Path:
    """tests.verify.create_bad_sample_template_config_dir_bad_xtn function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    input_content = "not json"
    file_path = config_dir / "config_0.txt"
    file_path.write_text(input_content)
    return config_dir

