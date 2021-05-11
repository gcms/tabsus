import re
import fnmatch
import zipfile
from pathlib import Path
import os.path


class Resource:
    """Refers to a file/object reference that can be opened for reading"""

    def open(self):
        """Open the resource, returning a closable object that can be used for reading as a binary file"""
        pass


class FileLoader:
    def load(self, path):
        """Loads a conversion file (CNV/DBF) from a relative path"""
        pass

    @classmethod
    def open(cls, path):
        if os.path.isfile(path) and (path.lower().endswith('.zip') or zipfile.is_zipfile(path)):
            return ZipFileLoader(path)
        elif os.path.isdir(path):
            return FileSystemLoader(path)

        raise NotImplementedError(f"Unsupported file type for {path}")


def unix_path(path):
    return path.replace('\\', '/')


def case_insensitive_dir_get(dir_path, file):
    case_insensitive_file = file.casefold()
    for f in os.listdir(dir_path):
        if f.casefold() == case_insensitive_file:
            return os.path.join(dir_path, f)

    return None


def case_insensitive_resolve_path(base, path):
    path_parts = path.split('/')
    cur_path = base
    for part in path_parts:
        cur_path = case_insensitive_dir_get(cur_path, part)
        if not cur_path:
            return None

    return cur_path


class FileSystemLoader(FileLoader):
    def __init__(self, path):
        self.root = path

    def load(self, path):
        file_path = case_insensitive_resolve_path(self.root, path)
        return FileResource(file_path) if file_path else None

    def list_files(self, glob):
        regex = re.compile(fnmatch.translate(glob), re.IGNORECASE)
        return [f.name for f in Path(self.root).rglob('*') if regex.match(f.name)]


class FileResource(Resource, os.PathLike):
    def __init__(self, file_path):
        self.file_path = file_path

    def open(self):
        return open(self.file_path, mode="rb")

    def __fspath__(self):
        return self.file_path

    def __str__(self):
        return self.file_path


class ZipFileLoader(FileLoader):
    def __init__(self, zip_file):
        if not isinstance(zip_file, zipfile.ZipFile):
            zip_file = zipfile.ZipFile(zip_file)

        self.zip_file = zip_file

    def load(self, path):
        case_insensitive_path = path.casefold()
        for f in self.zip_file.infolist():
            if f.filename.casefold() == case_insensitive_path:
                return ZipResource(self.zip_file, f)

        return None

    def list_files(self, glob):
        regex = re.compile(fnmatch.translate(glob), re.IGNORECASE)
        return [f.filename for f in self.zip_file.infolist() if regex.match(f.filename)]


class ZipResource(Resource, os.PathLike):
    def __init__(self, zip_file, zip_info):
        self.zip_file = zip_file
        self.zip_info = zip_info

    def open(self):
        return self.zip_file.open(self.zip_info, mode='r')

    def __fspath__(self):
        return self.zip_info.filename

    def __str__(self):
        return f"{self.zip_file.filename}!{self.zip_info.filename}"
