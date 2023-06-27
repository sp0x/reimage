import os
from typing import Optional
from datetime import datetime, timezone

from reimage.utils import is_processable, get_output_filepath_misc, get_output_filepath, ProgressStat, print_progress_bar, \
    get_earliest_creation
from reimage.file_utils import move_to_dest, copy_to_dest, create_directory

# Mapping between device models and time zones
model_timezones = {
    "nikon d5600": "Asia/Tokyo",
}


def copy_misc_file(source: str, base_path, output_path, move_instead_of_copy: bool = False) -> str:
    new_filepath = get_output_filepath_misc(base_path, source, output_path)
    create_directory(os.path.dirname(new_filepath))
    if move_instead_of_copy:
        move_to_dest(source, new_filepath)
    else:
        copy_to_dest(source, new_filepath)
    return new_filepath


def move_file(source: str,
              base_path: str,
              base_output_directory: str,
              move_instead_of_copy: bool = False,
              should_match_extension: str = '.jpg') -> Optional[str]:
    filename = os.path.basename(source)
    _, extension = os.path.splitext(filename)

    if not is_processable(source, should_match_extension):
        # Non processable files are just copied/moved
        return copy_misc_file(source, base_path, base_output_directory, move_instead_of_copy)

    earliest_time = get_earliest_creation(source, model_timezones)
    if earliest_time == 0:
        print("Couldn't get creation time for %s" % source)
        return copy_misc_file(source, base_path, base_output_directory, move_instead_of_copy)

    c_time = datetime.fromtimestamp(earliest_time, tz=timezone.utc).astimezone()
    new_filepath = get_output_filepath(base_path, source, c_time, base_output_directory)
    create_directory(os.path.dirname(new_filepath))
    if move_instead_of_copy:
        move_to_dest(source, new_filepath, c_time)
    else:
        copy_to_dest(source, new_filepath, c_time)
    return new_filepath
