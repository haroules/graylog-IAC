"""tests.setup setup_common module"""
import json
from pathlib import Path

def create_empty_config_dir(base_dir: Path, name: str) -> Path:
    """tests.setup.create_empty_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    return config_dir

def create_bad_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    """test.setup.create_bad_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.json"
        file_path.write_text("some not json text")
    return config_dir

def create_bad_sample_stream_config_dir(base_dir: Path, name: str, file_count: int = 1) -> Path:
    """tests.setup.create_bad_sample_stream_config_dir function"""
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
    """tests.setup.create_bad_2_sample_stream_config_dir function"""
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
