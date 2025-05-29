import os
import sys
import shutil
from typing import List, Tuple, Union
from datetime import datetime

def generate_timestamp() -> str:
    str_timestamp = datetime.now().strftime("%m-%d-%Y-%H%M%S") 
    return str_timestamp
    
def list_existing_backups(str_backup_dir: str) -> int:
    try:
        list_backup_folders = os.listdir(str_backup_dir)
        return sum(1 for name in list_backup_folders if "backup-" in name)
    except FileNotFoundError as e:
        print(f"[ERROR] Failed listing backup folders: '{str_backup_dir}'. Error was: {e}")
        raise
    except os.error as e:
        print(f"[ERROR] Failed listing backup folders: '{str_backup_dir}'. Error was: {e}")
        raise

def create_backup_folder(base_path: str, timestamp: str, bool_verbose: bool) -> Tuple[bool, str]:
    try:
        backup_folder_name = f"backup-{timestamp}"
        backup_folder_path = os.path.join(base_path, backup_folder_name)
        if(bool_verbose): print(f"  Creating backup directory: '{backup_folder_path}'")
        os.makedirs(backup_folder_path, exist_ok=False)
    except FileExistsError:
        print(f"[ERROR] Directory '{backup_folder_path}' already exists.")
        raise
    except FileNotFoundError:
        print(f"[ERROR] A parent directory in '{backup_folder_path}' does not exist.")
        raise
    except os.error as e:
        print(f"[ERROR] An OSError occurred: {e}")
        raise
    
    return True, backup_folder_path

def copy_directories(directories: List[str], dest_base: str, bool_verbose: bool):
    try:
        for source in directories:
            folder_name = os.path.basename(source)
            dest = os.path.join(dest_base, folder_name)
            shutil.copytree(source, dest)
            if(bool_verbose): print(f"  Copied '{source}' to '{dest}'")
    except OSError as e:
        print(f"[ERROR]: OS related error: {e}")
        sys.exit(1)

def make_config_backup(args: List[str], config_dirs: List[str]) -> Tuple[bool, str]:
    # make a clean backup copy of all config objects that may get overwritten 
    # with nodeid, or indexid, or may just get messed up (point in time)
    # create timestamp and store as formatted string
    # create backup folder name incorporating time stamp
    # make backup folder directory on filesystem
    # create list of items to backup
    # iterate over list of items to backup copying one folder at a time
    # get top level folder name of source and create destination path of backup folder + source folder name
    # do the copy, print out success or error
    # TODO: verify count of files and dirs in backup folder match what was expected to be backed up
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
        print(f"Making safe copy of config files before modification in dir: '{str_pth_cwd}' with timestamp: '{str_timestamp}'")
        # create top level backup folder
        tuple_fnctn_returnval: Tuple[bool,str] = create_backup_folder(str_pth_cwd,str_timestamp, bool_verbose)
        bool_create_succes, str_path_or_message = tuple_fnctn_returnval
        # copy the subfolders to backup directory
        if(bool_create_succes):
            copy_directories(config_dirs, str_path_or_message, bool_verbose)
        else:
            return False, str_path_or_message
    except RuntimeError as e:
        return False, f"[ERROR] An runtime error occurred: {e}"
    except Exception as e:
        return False, f"[ERROR] An generic exception occurred: {e}"
    
    print("[Done] Making a safe copy of config files.\n")
    return True, str_path_or_message