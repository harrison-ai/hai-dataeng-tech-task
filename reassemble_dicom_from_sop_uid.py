"""
Description:
Receive a single dicom sop uid, retrieve the corresponding header & pixel information from a directory of tars, then reassemble & save the dicom.
"""

import argparse
import tarfile
from typing import Optional
from pathlib import Path

from reassemble_dicom import reassemble_dicom


def get_sop_uid_from_cli() -> str:
    parser = argparse.ArgumentParser(description="Dicom SOP UID")
    parser.add_argument(
        "--sop_uid", help="SOP UID of the DICOM", type=str, required=True
    )
    args = parser.parse_args()

    return args.sop_uid


def get_from_tar(tar_filename: Path, search_filename: str) -> Optional[bytes]:
    with tarfile.open(tar_filename, "r") as tar:
        for item in tar.getmembers():
            if item.name == search_filename:
                return tar.extractfile(item).read()
    return None


def search_tars_in_directory(directory: Path, search_filename: str) -> bytes:
    for tar_file in directory.glob("*.tar"):
        result = get_from_tar(tar_file, search_filename)
        if result:
            return result

    raise ValueError(f"{search_filename} not found in directory {directory}")


def reassemble_dicom_from_sop_uid(sop_uid: str) -> bytes:
    json_file = search_tars_in_directory(
        directory=json_dir, search_filename=f"{sop_uid}.json"
    )

    image_file = search_tars_in_directory(
        directory=image_dir, search_filename=f"{sop_uid}.j2c"
    )

    return reassemble_dicom(headers=json_file, pixel_data=image_file)


if __name__ == "__main__":
    # These 3 could be CLI inputs
    out_dir = Path("reassembled_dicoms")
    json_dir = Path("data/text")
    image_dir = Path("data/images")

    sop_uid = get_sop_uid_from_cli()
    dicom_bytes = reassemble_dicom_from_sop_uid(sop_uid)

    out_dir.mkdir(exist_ok=True)
    output_path = out_dir / f"{sop_uid}.dcm"

    with output_path.open("wb") as f:
        f.write(dicom_bytes)
