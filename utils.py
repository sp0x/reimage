import datetime
import os
import platform
from typing import Optional

import pytz
from PIL import ExifTags, Image


# Print iterations progress
def print_progress_bar(iteration,
                       total,
                       prefix='',
                       suffix='',
                       decimals=1,
                       length=100,
                       fill='█',
                       print_end="\r",
                       percentage=None):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percentage = iteration / float(total) if percentage is None else percentage
    percent = ("{0:." + str(decimals) + "f}").format(100 * percentage)
    filledLength = int(length * percentage)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if percentage == 1:
        print()


class ProgressStat:

    def __init__(self):
        self.processed_count = 0
        self.to_process_count = 0
        self._last_progress = 0

    def progress(self) -> float:
        p = min(1, int(self.processed_count / max(self.to_process_count, 1)))
        if self._last_progress > p:
            return self._last_progress
        self._last_progress = p
        return p


def localize_to_os_timezone(timestamp) -> datetime:
    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    return dt.astimezone()


def get_earliest_image_creation_timestamp(path) -> int:
    modified_datetime = modified_timestamp(path)
    created_datetime = creation_timestamp(path)
    exif_shutter_datetime = get_image_shot_on_timestamp(path)

    min_fs_datetime = min(modified_datetime, created_datetime)
    min_overall_datetime = min_fs_datetime
    if exif_shutter_datetime != 0:
        min_overall_datetime = min(min_fs_datetime, exif_shutter_datetime)

    return int(min_overall_datetime)


def get_image_shot_on_timestamp(path, src_timezone='Asia/Tokyo') -> int:
    exif_data = get_exif_data_from_image(path)
    if exif_data is None or exif_data.date_time_original is None:
        return 0
    # Localize to source timezone and convert to UTC
    dt = exif_data.date_time_original
    dt_with_tz = pytz.timezone(src_timezone).localize(dt)

    exif_shutter_datetime = dt_with_tz.astimezone(datetime.timezone.utc)
    return int(exif_shutter_datetime.timestamp())


class ExifData:

    def __init__(self):
        self.date_time_original = None


def get_exif_data_from_image(path) -> Optional[ExifData]:
    img = Image.open(path)
    img_exif = img.getexif()
    if img_exif is None:
        return None

    output = ExifData()
    date_format = "%Y:%m:%d %H:%M:%S"

    for key, val in img_exif.items():
        if key not in ExifTags.TAGS:
            continue
        exif_key = ExifTags.TAGS[key]

        if exif_key == "DateTimeOriginal":
            output.date_time_original = datetime.datetime.strptime(val, date_format)

    img.close()

    return output


def modified_timestamp(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getmtime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        return stat.st_mtime


def creation_timestamp(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime
