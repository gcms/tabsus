import os

import nocasedict

import tabsus
from tabsus.conversion.cnv import CnvParser
from tabsus.conversion.dbf import DbfParser
from tabsus.file_loader import FileLoader, unix_path


class ConversionLoader:
    """
    Reads and parses conversion files (CNV/DBF).
    """
    FILE_TYPES = {
        '.cnv': CnvParser,
        '.dbf': DbfParser
    }

    def __init__(self, file_loader, encoding):
        if not isinstance(file_loader, FileLoader):
            file_loader = FileLoader.open(file_loader)

        self.file_loader = file_loader
        self.encoding = encoding
        self.cnv_files = nocasedict.NocaseDict()

    def get(self, path):
        path = unix_path(path)

        cnv = self.cnv_files.get(path)
        if not cnv:
            cnv = self.load(path)
            self.cnv_files[path] = cnv

        return cnv

    def load(self, path, encoding=tabsus.DEFAULT_ENCODING):
        file_ext = os.path.splitext(path)[1].lower()

        parser_class = ConversionLoader.FILE_TYPES.get(file_ext)
        if parser_class:
            path = unix_path(path)
            with self.file_loader.load(path).open() as file:
                file_name = os.path.basename(path)
                encoding = encoding or self.encoding or tabsus.DEFAULT_ENCODING

                parser = parser_class(file, file_name, encoding)
                return parser.parse()
        else:
            raise NotImplementedError(f"File '{path}' is not supported."
                                      f"Supported types: {ConversionLoader.FILE_TYPES.keys()}")
