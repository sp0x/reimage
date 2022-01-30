"""
This module is a utility to copy image files
and rename them based on the time they were created or shot.
"""

import argparse
import os
from typing import Optional
from datetime import datetime, timezone

import file_utils
import utils

model_timezones = {
    "nikon d5600": "Asia/Tokyo",
}


def process_entry(entry: os.DirEntry,
                  base_path: str,
                  output_path: str,
                  move_instead_of_copy: bool = False) -> Optional[str]:
    _, extension = os.path.splitext(entry.name)
    earliest_time = utils.get_earliest_creation(entry.path, model_timezones)
    if earliest_time == 0:
        print("Couldn't get creation time for %s" % entry.path)
        return None

    c_time = datetime.fromtimestamp(earliest_time, tz=timezone.utc).astimezone()
    new_filepath = utils.get_output_filepath(base_path, entry.path, c_time, output_path)
    file_utils.create_directory(os.path.dirname(new_filepath))
    if move_instead_of_copy:
        file_utils.move_to_dest(entry.path, new_filepath, c_time)
    else:
        file_utils.copy_to_dest(entry.path, new_filepath, c_time)
    return new_filepath


def main():
    """
    Command line utility to reorder pictures based on  when they were created.
    """
    parser = argparse.ArgumentParser(description="Image file renaming utility.")
    parser.add_argument('-s', '--source', type=str, help="Source directory")
    parser.add_argument('-d', '--destination', type=str,
                        help="Destination directory. If not specified then an "
                             "`output` directory is created within the source "
                             "directory.")
    parser.add_argument('-r', '--recursive', type=bool, default=True)
    parser.add_argument('-x', '--extension', type=str, default='.jpg')
    parser.add_argument('--move', action='store_const', const=True, default=False,
                        help='Move instead of copying to output directory')

    args = parser.parse_args()
    input_path = args.source
    output_path = args.destination
    move_files = args.move
    if output_path is None:
        output_path = os.path.join(input_path, "output")
        file_utils.create_directory(output_path)

    recursive = args.recursive
    extension = str(args.extension).lower()

    progress_stat = utils.ProgressStat()
    for entry in file_utils.scantree(input_path, output_path, recursive, progress_stat):
        if not utils.is_processable(entry, extension):
            continue
        process_entry(entry, input_path, output_path, move_files)
        msg = f"Files processed {progress_stat.processed_count}/{progress_stat.to_process_count}"
        utils.print_progress_bar(progress_stat.processed_count,
                                 progress_stat.to_process_count,
                                 msg,
                                 percentage=progress_stat.progress())


if __name__ == "__main__":
    main()
