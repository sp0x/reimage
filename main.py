"""
This module is a utility to copy image files
and rename them based on the time they were created or shot.
"""

import argparse
import os
from typing import Optional

import file_utils
import utils


def process_entry(entry: os.DirEntry,
                  base_path: str,
                  should_match_extension: str,
                  output_path: str) -> Optional[str]:
    """
    Process scandir entries, copying the file if necessary
    """
    if not entry.is_file():
        return None

    _, extension = os.path.splitext(entry.name)
    if extension.lower() != should_match_extension.lower():
        print("Skipping: %s" % entry)
        return None

    earliest_time = utils.get_earliest_image_creation_timestamp(entry.path)
    if earliest_time == 0:
        print("Couldn't get creation time for %s" % entry.path)
        return None
    c_time = utils.localize_to_os_timezone(earliest_time)
    new_filename = f'{c_time.year}_{c_time.month}_{c_time.day}_' \
                   f'{c_time.hour}_{c_time.hour}_{c_time.minute}_{c_time.second}' \
                   f'{extension}'
    entry_base_path = os.path.dirname(entry.path)
    new_subdirectory = entry_base_path.replace(base_path.rstrip(os.sep), '', 1).lstrip(os.sep)
    new_filepath = os.path.join(output_path, new_subdirectory, new_filename)
    file_utils.create_directory(os.path.dirname(new_filepath))
    file_utils.copy_to_dest(entry.path, new_filepath, c_time)
    return new_filepath


def main():
    """
    Command line utility
    """
    parser = argparse.ArgumentParser(description="Image file renaming utility.")
    parser.add_argument('-s', '--source', type=str, help="Source directory")
    parser.add_argument('-d', '--destination', type=str, help="Destination directory")
    parser.add_argument('-r', '--recursive', type=bool, default=True)
    parser.add_argument('-x', '--extension', type=str, default='.jpg')

    args = parser.parse_args()
    input_path = args.source
    output_path = args.destination
    if output_path is None:
        output_path = os.path.join(input_path, "output")
        file_utils.create_directory(output_path)

    recursive = args.recursive
    extension = str(args.extension).lower()

    progress_stat = utils.ProgressStat()
    for entry in file_utils.scantree(input_path, output_path, recursive, progress_stat):
        process_entry(entry, input_path, extension, output_path)
        msg = f"Files processed {progress_stat.processed_count}/{progress_stat.to_process_count}"
        utils.print_progress_bar(progress_stat.processed_count,
                                 progress_stat.to_process_count,
                                 msg,
                                 percentage=progress_stat.progress())


if __name__ == "__main__":
    main()
