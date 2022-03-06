import datetime
import os
import platform
from typing import Optional

import PIL
import pytz
from PIL import ExifTags, Image


def get_output_filepath_misc(base_input_path: str, file_path: str, output_path: str):
    _, extension = os.path.splitext(file_path)
    new_filename = os.path.basename(file_path)

    entry_base_path = os.path.dirname(file_path)
    new_subdirectory = entry_base_path.replace(base_input_path.rstrip(os.sep), '', 1).lstrip(os.sep)
    return os.path.join(output_path, new_subdirectory, new_filename)


def get_output_filepath(base_input_path: str, image_path: str, creation_time: datetime, output_path: str) -> str:
    _, extension = os.path.splitext(image_path)
    new_filename = f'{creation_time.year}_{creation_time.month}_{creation_time.day}_' \
                   f'{creation_time.hour}_{creation_time.minute}_{creation_time.second}' \
                   f'{extension}'
    entry_base_path = os.path.dirname(image_path)
    new_subdirectory = entry_base_path.replace(base_input_path.rstrip(os.sep), '', 1).lstrip(os.sep)
    new_filepath = os.path.join(output_path, new_subdirectory, new_filename)
    if os.path.exists(new_filepath):
        new_filepath = get_extra_filename(new_filepath)
    return new_filepath


def get_extra_filename(path: str) -> str:
    i = 1
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    name, extension = os.path.splitext(filename)
    while True:
        new_filename = name + f"_{i}{extension}"
        new_path = os.path.join(directory, new_filename)
        i += 1
        if not os.path.exists(new_path):
            return new_path


def is_processable(path: str, should_match_extension: str):
    """
    Process scandir entries, copying the file if necessary
    """
    if not os.path.isfile(path):
        return False

    filename = os.path.basename(path)
    _, extension = os.path.splitext(filename)
    if extension.lower() != should_match_extension.lower():
        return False

    return True


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
        p = min(1.0, self.processed_count / max(self.to_process_count, 1))
        self._last_progress = p
        return p


def localize_to_os_timezone(timestamp) -> datetime:
    dt = datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc)
    return dt.astimezone()


def get_earliest_creation(path, timezone_map: dict) -> int:
    modified_datetime = modified_timestamp(path)
    created_datetime = creation_timestamp(path)
    exif_shutter_datetime = get_image_shot_on_timestamp(path, timezone_map)

    min_fs_datetime = min(modified_datetime, created_datetime)
    min_overall_datetime = min_fs_datetime
    if exif_shutter_datetime != 0:
        min_overall_datetime = min(min_fs_datetime, exif_shutter_datetime)

    return int(min_overall_datetime)


def get_image_shot_on_timestamp(path: str, timezone_map: dict) -> int:
    """
    Gets the UTC timestamp of when a picture was shot.
    If a device model can't be mapped to a timezone, the current timezone is used.

    :param str path: The path to the image
    :param dict timezone_map: A map of device model: timezone. For example { 'nikon d5600': 'Asia/Tokyo' }
    :return: timestamp
    :rtype: int
    """
    exif_data = get_exif_data_from_image(path)
    if exif_data is None or exif_data.date_time_original is None:
        return 0
    # Localize to source timezone and convert to UTC
    dt = exif_data.date_time_original
    src_timezone = timezone_map[exif_data.model] if exif_data.model in timezone_map else None
    if src_timezone is not None:
        dt_with_tz = pytz.timezone(src_timezone).localize(dt)
    else:
        dt_with_tz = dt.astimezone()

    exif_shutter_datetime = dt_with_tz.astimezone(datetime.timezone.utc)
    return int(exif_shutter_datetime.timestamp())


class ExifData:

    def __init__(self):
        self.date_time_original = None
        self.model = None


def get_exif_data_from_image(path: str) -> Optional[ExifData]:
    try:
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
            elif exif_key == "Model":
                output.model = str(val).lower()

        img.close()

        return output
    except PIL.UnidentifiedImageError:
        return None


def modified_timestamp(path_to_file: str) -> float:
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


def creation_timestamp(path_to_file: str) -> int:
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return int(os.path.getctime(path_to_file))
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return int(stat.st_mtime)
