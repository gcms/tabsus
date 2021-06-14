import os
import logging

from tabsus.definition import DefIncrement, DefDimension, DefFile

from tabsus.parse_helper import strip_comments


class DefParser:
    def __init__(self, file, name=None, ignore_errors=True):
        self.ignore_errors = ignore_errors

        if name is None and hasattr(file, 'name'):
            name = os.path.basename(file.name)

        self.file = file
        self.name = name

        self.description = None
        self.file_pattern = None
        self.help_file = None
        self.variables = []

    def parse(self):
        self.description = None
        self.file_pattern = None
        self.variables = []

        for i, line in enumerate(self.file.readlines()):
            try:
                self.parse_line(line)
            except Exception as e:
                if not self.ignore_errors:
                    raise e
                else:
                    logging.error(f"Error in line {i}: {line}. {e}")

        return DefFile(self.name, self.description, self.variables, self.file_pattern, self.help_file)

    def parse_line(self, line):
        if line.strip().startswith(';') and not self.description:
            self.description = line.strip(' ;').rstrip()
            return

        if line.strip().startswith('A'):
            self.file_pattern = line.strip()[1:]
            return

        if line.strip().startswith('?'):
            self.help_file = line.strip()[1:]
            return

        line = strip_comments(line)
        if not line.strip():
            return

        if "LINHA_COMENTARIO" in line:
            return

        var_type = line[0].upper()
        parts = [var_type] + \
            list(map(lambda s: s.strip(), line[1:].split(',')))

        if var_type == 'I' or var_type == 'E':
            self.variables += [DefIncrement(var_type, parts[1], parts[2])]
        elif var_type == 'G':
            self.variables += [DefIncrement(var_type, parts[1], parts[1])]
        elif var_type == 'X' and parts[1].startswith('*'):
            return
        elif var_type in ['L', 'C', 'X', 'T', 'S', 'D', 'Q']:
            self.variables += [DefDimension(*parts)]
        elif var_type in ['F', 'H', 'R']:
            # HTML content and other unused variables
            pass
        else:
            logging.warning(f"Unknown variable type '{var_type}' in {line}")

        return
