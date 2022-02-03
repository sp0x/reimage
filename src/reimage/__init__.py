"""
-*- coding: utf-8 -*-
This module is a utility to copy image files
and rename them based on the time they were created or shot.
"""

import argparse
import os
from datetime import datetime, timezone
from typing import Optional

from reimage.utils import is_processable, get_output_filepath_misc, get_output_filepath, ProgressStat, print_progress_bar, \
    get_earliest_creation
from reimage.file_utils import move_to_dest, copy_to_dest, create_directory, scantree

model_timezones = {
    "nikon d5600": "Asia/Tokyo",
}


def copy_misc_file(entry: os.DirEntry, base_path, output_path, move_instead_of_copy: bool = False) -> str:
    new_filepath = get_output_filepath_misc(base_path, entry.path, output_path)
    create_directory(os.path.dirname(new_filepath))
    if move_instead_of_copy:
        move_to_dest(entry.path, new_filepath)
    else:
        copy_to_dest(entry.path, new_filepath)
    return new_filepath


def process_entry(entry: os.DirEntry,
                  base_path: str,
                  output_path: str,
                  move_instead_of_copy: bool = False,
                  should_match_extension: str = '.jpg') -> Optional[str]:
    _, extension = os.path.splitext(entry.name)

    if not is_processable(entry, should_match_extension):
        # Non processable files are just copied/moved
        return copy_misc_file(entry, base_path, output_path, move_instead_of_copy)

    earliest_time = get_earliest_creation(entry.path, model_timezones)
    if earliest_time == 0:
        print("Couldn't get creation time for %s" % entry.path)
        return copy_misc_file(entry, base_path, output_path, move_instead_of_copy)

    c_time = datetime.fromtimestamp(earliest_time, tz=timezone.utc).astimezone()
    new_filepath = get_output_filepath(base_path, entry.path, c_time, output_path)
    create_directory(os.path.dirname(new_filepath))
    if move_instead_of_copy:
        move_to_dest(entry.path, new_filepath, c_time)
    else:
        copy_to_dest(entry.path, new_filepath, c_time)
    return new_filepath


def main():
    """
    Command line utility to reorder pictures based on  when they were created.
    """
    parser = argparse.ArgumentParser(description="Image file organizing utility.")
    parser.add_argument('-s', '--source', type=str, help="Source directory", required=True)
    parser.add_argument('-d', '--destination', type=str,
                        help="Destination directory. If not specified then an "
                             "`output` directory is created within the source "
                             "directory.")

    parser.add_argument('-x', '--extension', type=str, default='.jpg',
                        help="File extension to use, by default this is .jpg")
    parser.add_argument('--recursive', action='store_const', const=True, default=False)
    parser.add_argument('--move', action='store_const', const=True, default=False,
                        help='Move instead of copying to output directory')

    args = parser.parse_args()
    input_path = args.source
    output_path = args.destination
    move_files = args.move
    if output_path is None:
        output_path = os.path.join(input_path, "output")
        create_directory(output_path)

    recursive = args.recursive
    should_match_extension = str(args.extension).lower()

    progress_stat = ProgressStat()
    for entry in scantree(input_path, output_path, recursive, progress_stat):
        process_entry(entry, input_path, output_path, move_files, should_match_extension)
        msg = f"Files processed {progress_stat.processed_count}/{progress_stat.to_process_count}"
        print_progress_bar(progress_stat.processed_count,
                           progress_stat.to_process_count,
                           msg,
                           percentage=progress_stat.progress())


if __name__ == "__main__":
    main()
