import datetime
import errno
import os
import time
from shutil import copy2, move

from ffcount import ffcount

from utils import ProgressStat

try:
    from os import scandir
except ImportError:
    from scandir import scandir  # use scandir PyPI module on Python < 3.5


def create_directory(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def copy_to_dest(source, dst, new_creation_dt: datetime.datetime):
    copy2(source, dst)
    timetuple = time.mktime(new_creation_dt.timetuple())
    os.utime(dst, (timetuple, timetuple))


def move_to_dest(source, dst, new_creation_dt: datetime.datetime):
    move(source, dst)
    timetuple = time.mktime(new_creation_dt.timetuple())
    os.utime(dst, (timetuple, timetuple))


def scantree(path, excluded_path, recursive=True, progress_stat: ProgressStat = None):
    """Recursively yield DirEntry objects for given directory."""
    if progress_stat is None:
        progress_stat = ProgressStat()

    file_count, dir_count = ffcount(path, False)
    progress_stat.to_process_count += file_count

    with scandir(path) as it:
        for entry in it:
            if entry.path == excluded_path:
                continue
            if recursive and entry.is_dir(follow_symlinks=False):
                # file_count, dir_count = ffcount(entry.path, False)
                # progress_stat.to_process_count += file_count
                # progress_stat.to_process_count += dir_count * 2
                yield from scantree(entry.path, excluded_path, recursive, progress_stat)  # see below for Python 2.x
            else:
                progress_stat.processed_count += 1
                yield entry
