import logging
import re
from io import TextIOWrapper

import tabsus

from tabsus.conversion import CategoryValue
from tabsus.conversion.cnv import CnvConversionFile, CnvCategory
from tabsus.conversion.cnv.lookup import *
from tabsus.parse_helper import strip_comments


class CnvParseException(Exception):
    pass


class CnvParser:
    def __init__(self, file, name=None, encoding=tabsus.DEFAULT_ENCODING):
        if not isinstance(file, TextIOWrapper):
            file = TextIOWrapper(file, encoding, line_buffering=True)

        self.file = file
        self.name = name if name else self.file.name

        self.current_line_no = 0
        self.current_line = None
        self.description = None

        self.format = None
        self.n_lines = None
        self.length = None
        self.type = None
        self.lines = None
        self.line_pattern = CnvParser.LINE_PATTERN

        self.errors = []
        self.has_range = False
        self.only_numeric_values = True
        self.all_single_value = True

    def parse(self):
        self.parse_header()

        self.lines = [None for _ in range(self.n_lines)]
        self.parse_body()
        if None in self.lines:
            missing = self.lines.index(None)
            logging.error(f"Invalid file {self.name}! Missing category {missing + 1}."
                          + f" {self.n_lines} categories in the header don't match the actual categories")

        return CnvConversionFile(self.name, self.description, self.n_lines, self.length, self.lines,
                                 self.find_lookup_strategy())

    def find_lookup_strategy(self):
        if not self.has_range:
            if self.type[0:1] == 'F':
                assert self.all_single_value
                return CnvBinarySearchRange
            elif self.type == 'L':
                return CnvHashIndex
            elif self.length <= 3 and self.only_numeric_values:
                return CnvArrayIndex
        else:
            return CnvRangeTree

        return CnvLinearLookup

    HEADER_PATTERN = re.compile(r'([A-Z]*)\s*([0-9]+)\s+([0-9]+)\s*([A-Z]*)')

    def parse_header(self):
        header = strip_comments(self.skip_to_header())

        match = CnvParser.HEADER_PATTERN.match(header)
        if not match:
            raise self.raise_exception(f"Invalid header: {header}")

        self.format = match[1]
        self.n_lines = int(match[2])
        self.length = int(match[3])
        self.type = match[4]

        if self.format == 'N':
            self.line_pattern = CnvParser.LONG_LINE_PATTERN

    def skip_to_header(self):
        while True:
            line = self.file.readline()
            if not line:
                break

            self.count_line(line)

            line = line.strip()
            if not (line.startswith(';') or line.startswith(':')) and len(line) > 0:
                break

            if line.startswith(';') and len(line) > 0:
                if not self.description:
                    self.description = ''
                else:
                    self.description += '\n'

                self.description += line[1:].strip()

        return line

    def count_line(self, line):
        self.current_line = line
        self.current_line_no += 1

    def raise_exception(self, error):
        raise CnvParseException(
            f"Error in line {self.current_line_no}: {error}.{self.current_line}")

    def parse_body(self):
        while True:
            line = self.file.readline()

            if not line:
                break

            self.count_line(line)

            line = line.rstrip()
            line = line.rstrip("\x1a")
            line = strip_comments(line)
            if not line:
                continue

            if not re.sub(r'\\W', '', line):
                continue

            self.parse_line(line)

    LINE_PATTERN = re.compile(r"^([\s\d]{3})([\s\d]{4})\s(.{52})([0-9A-Za-z,\.\s\-]+)")
    LONG_LINE_PATTERN = re.compile(r"^([\s\d]{4})([\s\d]{5})\s(.{101})([0-9A-Za-z,\.\s\-]+)")

    def parse_line(self, line):
        match = self.line_pattern.match(line)

        if not match:
            self.raise_exception("Invalid line")

        subtotal = match[1].strip()
        order = match[2].strip()
        description = match[3].strip()
        values = self.parse_values(match[4].rstrip())

        self.add_line(subtotal, order, description, values)

    def add_line(self, subtotal, order, description, values):
        index = int(order) - 1

        category = self.lines[index]
        if category is None:
            category = CnvCategory(subtotal, order, description, values)
        else:
            self.all_single_value = False

            if category.description != description and not subtotal:
                logging.warning("Categories with the same order number but different description %s ('%s' != '%s')" %
                                (order, category.description, description))

            category = CnvCategory(category.subtotal, category.order, description, category.values + values)

        self.lines[index] = category

    def parse_values(self, values):
        return list(map(self.parse_value, values.split(',')))

    VALUE_PATTERN = re.compile(
        r"[0-9A-Za-z][0-9A-Za-z ]*\-[0-9A-Za-z][0-9A-Za-z ]*")

    def parse_value(self, value):
        if CnvParser.VALUE_PATTERN.match(value):
            self.has_range = True
            self.all_single_value = False

            values = value.split('-')
            return CategoryValue(*values)

        if value and not value.isdigit():
            self.only_numeric_values = False

        return CategoryValue(value) if value else None
