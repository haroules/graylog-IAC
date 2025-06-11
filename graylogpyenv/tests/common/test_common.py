"""tests.common test_common module"""
import json
from pathlib import Path

MOCK_HOST_DATA=[{
        "index_config_file":"index_samplehost.json",
        "index_title":"samplehost_title",
        "input_config_file":"input_samplehost.json",
        "input_title":"samplehost_title",
        "extractors_total":1,
        "extractors":[{
            "extractor_config_file" :"extractor.json",
            "extractor_title" : "some_extractor"
        }],
        "stream_config_file":"config_0.json",
        "stream_title":"samplehost_stream"
        }]

def static_outs():
    """ tests.common.static_outs function """
    return(
        "7 Data Dirs\n"
        "1 Schema files\n"
        "1 Host cfg files\n"
        "1 Host cfg templates\n"
        "2 Index config files\n"
        "1 Input config files\n"
        "1 Stream config files\n"
        "1 Extractor config files\n\n"
    )

def shared_asserts(capturedout,expectedout,evaluecode,etype) -> None:
    """tests.setup.shared_asserts function"""
    assert capturedout == expectedout
    assert evaluecode == 1
    assert etype == SystemExit

def create_sample_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    """tests.backup.create_sample_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.txt"
        file_path.write_text(f"This is file {i}")
    return config_dir

def create_sample_index_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    """tests.verify.create_sample_index_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        file_path.write_text(json.dumps({"title": "mock_index_{i}","id": "mock_id_{i}"}))
    return config_dir

def create_sample_input_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.verify.create_sample_input_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = ({"node": "node_id_string", "global": True, "title": "input_title_2"})
        file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_sample_host_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.verify.create_sample_host_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = {"hostname":"samplehost",
        "config_sets_total":1,
        "config_sets": MOCK_HOST_DATA
        }
        file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_sample_extractor_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.verify.create_sample_extractor_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        xtrctr_json_content = { "title": "xtrctr_title","extractor_type": "regex"}
        file_path.write_text(json.dumps(xtrctr_json_content,indent=2))
    return config_dir

def create_sample_stream_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.verify.create_sample_stream_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = {
            "index_set_id": "samplehost_index_setid",
            "title": "samplehost-stream",
        }
        file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir
