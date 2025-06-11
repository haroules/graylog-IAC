"""src.backup module """
import os
import shutil
from typing import List
from datetime import datetime

from src.helpers import exit_with_message

def generate_timestamp() -> str:
    """src.backup.generate_timestamp function"""
    str_timestamp = datetime.now().strftime("%m-%d-%Y-%H%M%S")
    return str_timestamp

def list_existing_backups(str_backup_dir: str) -> int:
    """src.backup.list_existing_backups function"""
    count = 0
    try:
        list_backup_folders = os.listdir(str_backup_dir)
        for name in list_backup_folders:
            if "backup-" in name:
                count +=1
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR] FileNotFoundError in list_existing_backups {e}",1)
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in list_existing_backups {e}",1)
    return count

def create_backup_folder(base_path: str, timestamp: str, bool_verbose: bool) -> str:
    """src.backup.create_backup_folder function"""
    try:
        backup_folder_name = f"backup-{timestamp}"
        backup_folder_path = os.path.join(base_path, backup_folder_name)
        if bool_verbose:
            print(f"  Creating backup directory: '{backup_folder_path}'")
        os.makedirs(backup_folder_path, exist_ok=False)
    except FileExistsError as e:
        exit_with_message(f"[ERROR] FileExistsError in create_backup_folder {e}",1)
    except FileNotFoundError as e:
        exit_with_message(f"[ERROR] FileNotFoundError in create_backup_folder {e}",1)
    except os.error as e:
        exit_with_message(f"[ERROR] An OSError occurred in create_backup_folder: {e}",1)
    return backup_folder_path

def copy_directories(directories: List[str], dest_base: str, bool_verbose: bool) -> None:
    """src.backup.copy_directories function"""
    try:
        for source in directories:
            folder_name = os.path.basename(source)
            dest = os.path.join(dest_base, folder_name)
            shutil.copytree(source, dest)
            if bool_verbose:
                print(f"  Copied '{source}' to '{dest}'")
    except os.error as e:
        exit_with_message(f"[ERROR]: An OSError occurred in copy_directories: {e}",1)

def make_config_backup(args: List[str], config_dirs: List[str]) -> str:
    """src.backup.make_config_backup function"""
    # make a clean backup copy of all config objects that may get overwritten
    # with nodeid, or indexid, or may just get messed up (point in time)
    # create timestamp and store as formatted string
    # create backup folder name incorporating time stamp
    # make backup folder directory on filesystem
    # create list of items to backup
    # iterate over list of items to backup copying one folder at a time
    # get top level folder name of source and create destination path of backup folder + source folder name
    # do the copy, print out success or error
    str_timestamp = ""                  # string formatted timestamp to create unique backups
    int_existing_backupfldr_count = 0

    # based on positional arguments we have to set cur working directory and bool_verbose
    str_pth_cwd = args[4] if len(args) == 5 else args[3]
    bool_verbose = True if len(args) == 4 else args[3]
     # check how many backups exist if 5 or more print message so we don't fill disk
    try:
        # get count of existing backup folders from list
        int_existing_backupfldr_count = list_existing_backups(str_pth_cwd)
        if int_existing_backupfldr_count >= 5:
            print("[WARNING] 5 or more backups already exist. You may want to purge some old ones.")
        # generate timestamp for foldername
        str_timestamp = generate_timestamp()
        print(f"Making backup copy of config files at: '{str_pth_cwd}' with timestamp: '{str_timestamp}'")
        # create top level backup folder
        str_path = create_backup_folder(str_pth_cwd,str_timestamp, bool_verbose)
        # copy the subfolders to backup directory
        copy_directories(config_dirs, str_path, bool_verbose)
        print("[Done] Making a backup copy of config files.\n")
    except RuntimeError as e:
        exit_with_message(f"[ERROR] An runtime error occurred in make_config_backup: {e}",1)
    return str_path
