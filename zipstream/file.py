from typing import Optional
import pathlib
import requests
import struct
import zlib
from .headers import LocalFileHeader


class ZipStreamFile:
    def __init__(
        self,
        url: str,
        filename: str,
        file_offset: int,
        file_size: int,
    ):
        self.url = url
        self.filename = filename
        self.file_offset = file_offset
        self.file_size = file_size

    def download(
        self,
        filename: Optional[str] = None,
        base_path: Optional[str] = None,
    ):
        struct_format = "<4sHHHHHIIIHH"
        struct_size = struct.calcsize(struct_format)
        headers = {
            "Range": f"bytes={self.file_offset}-{self.file_offset+struct_size-1}"
        }
        local_file_header = requests.get(self.url, headers=headers, stream=True).content
        local_file_header = LocalFileHeader(
            *struct.unpack(struct_format, local_file_header)
        )
        data_offset = (
            struct_size
            + local_file_header.file_name_length
            + local_file_header.extra_field_length
        )

        headers = {
            "Range": f"bytes={self.file_offset+data_offset}-{self.file_offset+data_offset+self.file_size-1}"
        }
        data = requests.get(self.url, headers=headers, stream=True).content
        if local_file_header.method == 8:
            data = zlib.decompress(data, -15)
        elif local_file_header.method != 0:
            raise ValueError("Unsupported compression method.")

        filename = filename or self.filename
        if base_path is not None and filename is not None:
            path = pathlib.Path(base_path) / filename
            _ = path.write_bytes(data)

        return data

    def __repr__(self):
        return (
            f"ZipStreamFile(\n\t"
            f"url={self.url},\n\t"
            f"filename={self.filename},\n\t"
            f"file_offset={self.file_offset},\n\t"
            f"file_size={self.file_size}\n)"
        )
