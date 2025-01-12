import glob
from dataclasses import dataclass
from pathlib import Path, PosixPath, WindowsPath
from typing import List, Optional, Tuple

import boto3

from cu_pass.dpa_calculator.main_runner.results_recorder import LOG_EXTENSION
from testcases.cu_pass.dpa_calculator.features.helpers.utilities import delete_file, sanitize_output_log


def get_uploaded_log_content(bucket_name: str) -> str:
    uploaded_filepaths = get_s3_uploaded_filenames(bucket_name=bucket_name)
    uploaded_log_filepath = next(filepath for filepath in uploaded_filepaths if LOG_EXTENSION in filepath)
    return get_uploaded_file_content(bucket_name=bucket_name, object_name=uploaded_log_filepath)


def get_uploaded_file_content(bucket_name: str, object_name: str) -> str:
    s3 = boto3.client('s3')
    uploaded_file_local_filepath = 'tmp'
    try:
        matching_uploaded_name = _get_object_name_ignoring_runtime(bucket_name=bucket_name, object_name=object_name)
        assert matching_uploaded_name, f'File {object_name} not found'
        s3.download_file(bucket_name, matching_uploaded_name, uploaded_file_local_filepath)
        output_content = sanitize_output_log(log_filepath=uploaded_file_local_filepath)
    finally:
        delete_file(filepath=uploaded_file_local_filepath)
    return output_content


def _get_object_name_ignoring_runtime(bucket_name: str, object_name: str) -> Optional[str]:
    object_name_without_runtime = _get_filepath_without_runtime(filepath=object_name)
    uploaded_names = get_s3_uploaded_filenames(bucket_name=bucket_name)
    for uploaded_name in uploaded_names:
        uploaded_name_without_runtime = _get_filepath_without_runtime(filepath=uploaded_name)
        if object_name_without_runtime == uploaded_name_without_runtime:
            return uploaded_name


def _get_filepath_without_runtime(filepath: str) -> str:
    parts = _get_parts_without_runtime(filepath=filepath)
    parts_without_runtime = list(parts.parts_before_runtime) + [parts.part_after_runtime]
    return parts.separator.join(parts_without_runtime)


def get_filepath_with_any_runtime(filepath: str) -> str:
    parts = _get_parts_without_runtime(filepath=filepath)
    parts_without_runtime = Path(*parts.parts_before_runtime, '*', parts.part_after_runtime)
    return glob.glob(str(parts_without_runtime))[0]


@dataclass
class PartsWithoutRuntime:
    parts_before_runtime: Tuple[str, ...]
    part_after_runtime: str
    separator: str


def _get_parts_without_runtime(filepath: str) -> PartsWithoutRuntime:
    parts = Path(filepath).parts
    return PartsWithoutRuntime(
        parts_before_runtime=parts[:-2],
        part_after_runtime=parts[-1],
        separator=WindowsPath._flavour.sep if WindowsPath._flavour.sep in filepath else PosixPath._flavour.sep
    )


def get_s3_uploaded_filenames(bucket_name: str) -> List[str]:
    s3 = boto3.client('s3')
    uploaded_contents = s3.list_objects(Bucket=bucket_name).get('Contents', [])
    return [key['Key'] for key in uploaded_contents]
