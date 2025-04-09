from typing import List, Optional, Tuple
import struct
import requests
from .headers import CentralDirectoryFileHeader
from .file import ZipStreamFile


class ZipStream:
    tail_size: int = 65536

    @staticmethod
    def size(url: str):
        headers = {"Range": f"bytes=-1"}
        return int(
            requests.get(url, headers=headers).headers["Content-Range"].split("/")[-1]
        )

    @classmethod
    def get_central_directory(self, url: str, offset: Optional[int] = None):
        headers = {"Range": f"bytes=-{self.tail_size}"}
        tail_data = requests.get(url, headers=headers, stream=True).content
        zip64_eocd = b"\x50\x4b\x06\x06"
        eocd_offset = tail_data.rfind(zip64_eocd)
        eocd = tail_data[eocd_offset:]
        cd_offset = int.from_bytes(eocd[48 : 48 + 8], byteorder="little")
        if offset is not None:
            cd_offset - offset
        headers = {"Range": f"bytes={cd_offset}-"}
        central_directory = requests.get(url, headers=headers, stream=True).content
        return central_directory

    @classmethod
    def get_files(self, url: str, central_directory: bytes, file_to_get: str = None):
        files = []
        offset = 0
        while offset <= len(central_directory):
            file, offset = ZipStream.get_file(
                url=url, central_directory=central_directory, offset=offset
            )
            if file is None:
                continue
            if file_to_get is None:
                files.append(file)
            elif file_to_get is not None and file_to_get in file.filename:
                return file
        return files

    @classmethod
    def get_file(self, url: str, central_directory: bytes, offset: int) -> Tuple[ZipStreamFile, int]:
        struct_format = "<4sHHHHHHIIIHHHHHII"
        struct_size = struct.calcsize(struct_format)
        buffer = central_directory[offset : offset + struct_size]
        if len(buffer) < struct_size:
            return None, offset + struct_size
        central_directory_file_header = CentralDirectoryFileHeader(
            *struct.unpack(struct_format, buffer)
        )
        filename = central_directory[
            offset
            + struct_size : offset
            + struct_size
            + central_directory_file_header.file_name_length
        ].decode("utf-8")
        if "/" in filename:
            filename = filename.split("/")[-1]
        next_offset = (
            offset
            + struct_size
            + central_directory_file_header.file_name_length
            + central_directory_file_header.extra_field_length
            + central_directory_file_header.file_comment_length
        )
        if not filename:
            return None, next_offset
        is_zip64 = (central_directory_file_header.compressed_size == 2**32 - 1) or (
            central_directory_file_header.relative_offset == 2**32 - 1
        )
        if is_zip64:
            extra = central_directory[
                offset
                + struct_size
                + central_directory_file_header.file_name_length : next_offset
            ]
            central_directory_file_header.relative_offset = int.from_bytes(
                extra[-8:], byteorder="little"
            )
        return (
            ZipStreamFile(
                url=url,
                filename=filename,
                file_offset=central_directory_file_header.relative_offset,
                file_size=central_directory_file_header.compressed_size,
            ),
            next_offset,
        )

    def __init__(
        self,
        url: str,
        central_directory: Optional[bytes] = None,
        offset: Optional[int] = None,
    ):
        self.url = url
        central_directory = central_directory or ZipStream.get_central_directory(
            url=self.url, offset=offset
        )
        self.central_directory = central_directory
        self.files: List[ZipStreamFile] = ZipStream.get_files(
            url=self.url, central_directory=self.central_directory
        )
