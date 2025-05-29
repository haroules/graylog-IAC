"""setup setup_common module"""
import json
from pathlib import Path

def create_sample_index_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    """setup create_sample_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        file_path.write_text(json.dumps({"title": "mock_index_{i}","id": "mock_id_{i}"}))
    return config_dir

def create_empty_index_config_dir(base_dir: Path, name: str) -> Path:
    """setup create_empty_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    return config_dir

def create_bad_sample_index_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    """setup create_bad_sample_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        file_path.write_text("some not json text")
    return config_dir

def create_sample_input_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup create_sample_input_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = ({"node": "node_id_string", "global": True, "title": "input_title_2"})
        file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_bad_sample_input_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup create_sample_input_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        file_path.write_text('bad_json')
    return config_dir

def create_sample_host_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup create_sample_host_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = {"hostname":"samplehost",
        "config_sets_total":1,
        "config_sets":[{
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
        "stream_title":"samplehost_stream"}]}
        file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_bad_sample_host_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup create_bad_sample_host_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = "bad json content"
        file_path.write_text(input_json_content)
    return config_dir

def create_sample_extractor_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup create_sample_extractor_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        xtrctr_json_content = { "title": "xtrctr_title","extractor_type": "regex"}
        file_path.write_text(json.dumps(xtrctr_json_content,indent=2))
    return config_dir

def create_bad_sample_extractor_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup create_bad_sample_extractor_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        xtrctr_json_content = "badjson"
        file_path.write_text(xtrctr_json_content)
    return config_dir

def create_sample_stream_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup create_sample_stream_config_dir function"""
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

def create_bad_sample_stream_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup create_bad_sample_stream_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        input_json_content = {
            "index_set_id_bad": "samplehost_index_setid",
            "title": "samplehost-stream",
        }
        file_path.write_text(json.dumps(input_json_content,indent=2))
    return config_dir

def create_bad_2_sample_stream_config_dir(base_dir: Path, name: str) -> Path:
    """tests.setup create_sample_stream_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    file_path = config_dir / "config_0.json"
    input_json_content = {
        "index_set_id_bad": "samplehost_index_setid",
        "title": "samplehost-stream",
    }
    file_path.write_text(json.dumps(input_json_content,indent=2))
    file_path = config_dir / "config_1.json"
    input_content = "bad_content"
    file_path.write_text(input_content)
    return config_dir
