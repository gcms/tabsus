from tabsus.conversion import Category, ConversionFile
from tabsus.conversion import CategoryValue
from nocasedict import NocaseDict
import dbfread


class DbfCategory(Category):
    def __init__(self, value, description):
        self.values = [value]
        self.description = description


class DbfConversionFile(ConversionFile):
    def __init__(self, name, fields, records):
        self.name = name
        self.default_field = fields[0]
        self.fields = set(fields)
        self.records = records
        self.indexes = NocaseDict({})

    def extract_value(self, def_var, record_access, record):
        return record_access.extract_field(record, def_var.field)

    def get_index_by(self, field):
        if field not in self.fields:
            field = self.default_field

        index = self.indexes.get(field)
        if not index:
            index = DbfIndex(field, self)
            self.indexes[field] = index

        return index

    def find_category(self, dimension, value):
        record = self.find_record(dimension.field, value)
        return DbfCategory(CategoryValue(value), record[dimension.dbf_field]) if record else None

    def find_record(self, field, value):
        index = self.get_index_by(field)
        return index[value]

    def get_categories(self, dimension):
        index = self.get_index_by(dimension.field)
        return index.get_categories(dimension.dbf_field)


class DbfIndex:
    def __init__(self, key_field, dbf_file):
        self.key_field = key_field
        self.dbf_file = dbf_file
        self.categories = NocaseDict({c[key_field]: c for c in dbf_file.records})

    def __getitem__(self, key):
        return self.categories.get(key)

    def __contains__(self, key):
        return self[key]

    def get_categories(self, field):
        return [DbfCategory(key, r[field]) for key, r in self.categories.items()]


class DbfParser:
    def __init__(self, file, name, encoding):
        self.file = file
        self.name = name
        self.encoding = encoding

    def parse(self):
        reader = DbfReader(self.file, self.encoding)

        fields = [f.name for f in reader.fields]
        records = [r for r in reader]

        return DbfConversionFile(self.name, fields, records)


class DbfReader(dbfread.DBF):
    """Overrides dbfread.DBF to enable reading from an open file handle,
     (e.g. compressed file, zip entry) instead of a file system file"""

    def __init__(self, infile, encoding):
        self.encoding = None
        self.ignorecase = True
        self.lowernames = False
        self.parserclass = dbfread.FieldParser
        self.raw = False
        self.ignore_missing_memofile = False
        self.char_decode_errors = 'strict'

        import collections
        self.recfactory = NocaseDict

        # Name part before .dbf is the table name
        self._records = None
        self._deleted = None

        # Filled in by self._read_headers()
        self.header = None
        self._read_header(infile)

        if self.encoding is None or self.encoding.lower() == 'ascii':
            if encoding:
                self.encoding = encoding
        self.fields = []  # namedtuples
        self.field_names = []  # strings
        self._read_field_headers(infile)
        self._check_headers()
        self.infile = infile
        self.memofilename = self._get_memofilename()

        self._records = list(self._iter_records(b' '))

    def _iter_records(self, record_type=b' '):
        infile = self.infile
        with self._open_memofile() as memofile:

            if not self.raw:
                field_parser = self.parserclass(self, memofile)
                parse = field_parser.parse

            # Shortcuts for speed.
            skip_record = self._skip_record
            read = infile.read

            while True:
                sep = read(1)

                if sep == record_type:
                    if self.raw:
                        items = [(field.name, read(field.length)) \
                                 for field in self.fields]
                    else:
                        items = [(field.name,
                                  parse(field, read(field.length))) \
                                 for field in self.fields]

                    yield self.recfactory(items)

                elif sep in (b'\x1a', b''):
                    # End of records.
                    break
                else:
                    skip_record(infile)
