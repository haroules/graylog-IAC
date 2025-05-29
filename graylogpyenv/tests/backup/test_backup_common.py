"""tests.backup backup_common module"""
from pathlib import Path

def create_sample_config_dir(base_dir: Path, name: str, file_count: int = 2) -> Path:
    """tests.backp create_sample_config_dir function"""
    config_dir = base_dir / name
    config_dir.mkdir()
    for i in range(file_count):
        file_path = config_dir / f"config_{i}.txt"
        file_path.write_text(f"This is file {i}")
    return config_dir
