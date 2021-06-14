class DefVariable:
    """
    Represents a column, row or selection described in a DEF file.

    Documentation in: ftp://ftp.datasus.gov.br/tabnet/doc/Definicao.pdf
    """

    def __init__(self, var_type, name, field):
        self.var_type = var_type
        self.name = name
        self.original_field = field
        self.field = field[0:10]

    def __str__(self):
        return f"{self.var_type}{self.name}, {self.field}"

    def __repr__(self):
        return str(self)

    def transform(self, def_access, record):
        pass

    def map(self, def_access, value):
        pass


class DefIncrement(DefVariable):
    """Represents an increment variable"""

    # Could include 3 extra information (divisor, scale factor, and decimals precision)
    def __init__(self, var_type, name, field):
        DefVariable.__init__(self, var_type, name, field)

    def transform(self, def_access, record):
        return def_access.get_value(self, record)

    def map(self, def_access, value):
        return value


class DefDimension(DefVariable):
    """Represents a dimension/classification variable"""

    def __init__(self, var_type, name, field, start, cnv_filename, col_dbf=None, file_dbf=None):
        DefVariable.__init__(self, var_type, name, field)

        self.start = None
        self.dbf_field = None

        if start.isdigit():
            self.start = int(start) - 1
        else:
            self.dbf_field = start

        self.cnv_filename = cnv_filename

    def __str__(self):
        return f"{self.var_type}{self.name}, {self.field}, {self.start}, {self.cnv_filename}"

    def transform(self, def_access, record):
        """Extracts the value from the record and convert to the corresponding category."""
        return def_access.get_category(self, record)

    # def map(self, def_access, value):
    #     return def_access.map(self, value)

    def get_mapping(self, def_access):
        """Returns the available categories for this variable."""
        cnv_file = def_access.get_cnv(self)
        return cnv_file.get_categories(self)


class DefFile:
    """
    Represents a parsed DEF file according to the documentation.
    ftp://ftp.datasus.gov.br/tabnet/doc/Definicao.pdf
    """

    def __init__(self, name, description, variables, file_pattern, help_file):
        self.name = name
        self.description = description
        self.variables = variables
        self.file_pattern = file_pattern
        self.help_file = help_file

    def __contains__(self, key):
        try:
            return self[key] is not None
        except IndexError(f"Variable {key} not in {[v.name for v in self.variables]}"):
            return False

    def __getitem__(self, key):
        for var in self.variables:
            if var.name == key:
                return var

        raise IndexError(
            f"Variable {key} not in {map(lambda v: v.name, self.variables)}")

    def __repr__(self):
        return f"{self.name}" + ("" if not self.description else f" - {self.description}")

    def __str__(self):
        return f"{self.name}" + ("" if not self.description else f" - {self.description}")


class DefFileContext:
    """Abstracts access to a DEF file and it's context (cnv loader, record access)"""

    def __init__(self, def_file, cnv_loader, record_access):
        self.def_file = def_file
        self.cnv_loader = cnv_loader
        self.record_access = record_access

    def get_cnv(self, dimension):
        """
        Loads a conversion file (CNV/DBF)
        :param dimension: a DefDimension
        :return: a ConversionFile obtained by parsing cnv_filename
        """
        return self.cnv_loader.get(dimension.cnv_filename)

    def get_value(self, variable, record):
        return self.record_access.extract_field(record, variable.field)

    def get_category(self, dimension, record):
        cnv_file = self.get_cnv(dimension)
        value = cnv_file.extract_value(dimension, self.record_access, record)

        def map_to_category(v):
            category = cnv_file.find_category(dimension, v)
            return category.description if category else None

        return self.record_access.map(value, map_to_category)
