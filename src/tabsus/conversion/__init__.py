class RecordAccess:
    """
    Abstract access to records, enabling to use different kinds of records/record sources
     (e.g. dictionaries, dataframes, byte arrays, etc).

     When converting raw records to categories some conversions may be based on values from more than one field.
     The conversion information available in CNV/DEF files only specifies the first field, the starting position
     and the value length. If the value length extends beyond the first field length the following bytes should
     be read from the following fields.
     """

    def extract_range(self, record, field_name, start, length):
        """
        Returns the value starting at record[field_name][start] reading up to length chars (bytes)
        :param record: record data structure
        :param field_name: starting field name
        :param start: starting position in the field named field_name
        :param length: number of chars to be read from the record
        :return: the value extracted from the record from the starting position in the starting field
        """
        pass

    def extract_field(self, record, field_name):
        """
        Returns the value of field_name field in record
        :param record: a record
        :param field_name: a field_name
        :return: value of field_name field in record
        """
        pass

    def map(self, value, fn):
        """
        Applies function fn to value. Different datastructures (e.g. dataseries/dataframes) may use different ways
        of applying a function.
        :param value: value returned by one of extract*() methods
        :param fn: function to be applied
        :return: fn(value)
        """
        pass


class Category:
    """
    Represents a category in a CNV/DBF file. Each category has a name, and a set of values which match with the category.
    """

    def __str__(self):
        return f"'{self.category}': [ {', '.join([str(v) for v in self.values])} ]"


class CategoryValue:
    """
    Represents a category value, which can be a single value, or a range of values.
    """

    def __init__(self, start, end=None):
        if end is None:
            if isinstance(start, tuple) and len(start) >= 2:
                start, end = start
            elif isinstance(start, range):
                start, end = start.start, start.stop
            else:
                end = start

        self.start = start
        self.end = end

    @property
    def is_single_valued(self):
        return self.start == self.end

    @property
    def is_empty(self):
        return self.is_single_valued and not self.start.strip()

    @property
    def value(self):
        if not self.is_single_valued:
            raise NotImplementedError(
                f"Single value not supported in category range {self}")

        return self.start

    @property
    def stop(self):
        # python ranges doesn't support closed (inclusive) upper-bound so we add this
        # helper function to change the string to the next lexicographic one
        if isinstance(self.end, str):
            return self.end[0:-1] + chr(ord(self.end[-1]) + 1)
        else:
            return self.end + 1

    def __contains__(self, value):
        return self.start <= value <= self.end

    def __str__(self):
        return self.value if self.is_single_valued else f"{self.start}-{self.end}"


class ConversionFile:
    """
    Represents a conversion file, which can be either a CNV/DBF file.

    Documentation is available in:

    ftp://ftp.datasus.gov.br/tabnet/doc/Definicao.pdf
    ftp://ftp.datasus.gov.br/tabnet/doc/Conversao.pdf
    """

    def extract_value(self, def_var, record_access, record):
        pass

    def find_category(self, dimension, value):
        """
        Returns the category matching the input value using the field specified in dimension
        :param dimension: a DefDimension defining the conversion variable
        :param value: the value to be converted to a category
        :return: the category corresponding to value or None if it doesn't match any category
        """
        pass

    def get_categories(self, dimension):
        """
        Returns all posible categories for a given dimension variable
        :param dimension: a DefDimension
        :return: list of categories
        """
        pass
