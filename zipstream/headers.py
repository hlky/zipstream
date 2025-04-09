from dataclasses import dataclass

@dataclass
class LocalFileHeader:
    signature: bytes
    version: int
    flag: int
    method: int
    modification_time: int
    modification_date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    file_name_length: int
    extra_field_length: int


@dataclass
class CentralDirectoryFileHeader:
    signature: bytes
    version: int
    minimum_version: int
    flag: int
    method: int
    modification_time: int
    modification_date: int
    crc32: int
    compressed_size: int
    uncompressed_size: int
    file_name_length: int
    extra_field_length: int
    file_comment_length: int
    disk_number: int
    internal_file_attributes: int
    external_file_attributes: int
    relative_offset: int
