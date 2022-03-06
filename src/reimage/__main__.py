"""
-*- coding: utf-8 -*-
This module is a utility to copy image files
and rename them based on the time they were created or shot.
"""

import argparse
import os
import sys

from reimage import move_file
from reimage.utils import ProgressStat, print_progress_bar
from reimage.file_utils import create_directory, scantree


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
                        help="File extension to use, by default this is .jpg. Note that non-matching")
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
        move_file(entry.path, input_path, output_path, move_files, should_match_extension)
        msg = f"Files processed {progress_stat.processed_count}/{progress_stat.to_process_count}"
        print_progress_bar(progress_stat.processed_count,
                           progress_stat.to_process_count,
                           msg,
                           percentage=progress_stat.progress())


if __name__ == "__main__":
    sys.exit(main())
