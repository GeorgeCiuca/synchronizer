import sys
import shutil
import logging
from time import sleep
import os


def grab_source_info():
    source = sys.argv[1]
    source_items = []
    for (dir_path, dir_names, file_names) in os.walk(source):
        for file in file_names:
            source_items.append([os.path.join(dir_path, file), os.stat(os.path.join(dir_path, file)).st_mtime])
    return source_items, source


def sync_files(source_items, source):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=[
        logging.FileHandler(sys.argv[4]), logging.StreamHandler(sys.stdout)])
    logging.info("Source folder synchronization started")
    replica = sys.argv[2]
    replica_items = []
    if not os.path.exists(replica):
        os.mkdir(replica)
    for (dir_path, dir_names, file_names) in os.walk(replica):
        for file in file_names:
            replica_items.append(os.path.relpath(os.path.join(dir_path, file), replica))
    copy_new_files(source_items,replica_items,replica,source)
    remove_files(source_items, replica_items, replica, source)
    logging.info("Source folder synchronization completed")


def copy_new_files(source_items, replica_items, replica, source):
    for item in source_items:
        if os.path.relpath(item[0], source) not in replica_items:
            replica_dst_dir = os.path.join(replica, os.path.relpath(os.path.dirname(item[0]), source))
            try:
                os.makedirs(replica_dst_dir)
            except FileExistsError:
                pass
            shutil.copy2(item[0], replica_dst_dir)
            logging.info(f"'{item[0]}' copied to replica folder.")
        else:
            if item[1] != os.stat(os.path.join(replica, os.path.relpath(item[0], source))).st_mtime:
                replica_dst_dir = os.path.join(replica, os.path.relpath(os.path.dirname(item[0]), source))
                try:
                    os.makedirs(replica_dst_dir)
                except FileExistsError:
                    pass
                shutil.copy2(item[0], replica_dst_dir)

def remove_files(source_items, replica_items, replica, source):
    current_items = [os.path.relpath(_item[0], source) for _item in source_items]
    for file in replica_items:
        if file not in current_items:
            os.remove(os.path.join(replica, file))
            logging.info(f"'{file}' removed from replica folder.")

def sync_period():
    try:
        sync_p = float(sys.argv[3])
        return sync_p
    except ValueError:
        print("Third command line argument should be a number")


if __name__ == '__main__':
    while True:
        source_items, source = grab_source_info()
        sync_files(source_items, source)
        sleep(sync_period())
