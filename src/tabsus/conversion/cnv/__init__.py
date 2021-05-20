from tabsus.conversion import ConversionFile, Category


class CnvConversionFile(ConversionFile):
    def __init__(self, name, description, n_lines, length, categories, lookup_method):
        self.name = name
        self.description = description
        self.n_lines = n_lines
        self.length = length
        self.categories = [c for c in categories if c and not c.subtotal]
        self.empty = ([c for c in categories if c and c.has_empty] or [None])[0]
        self.lookup = lookup_method(self)

    def extract_value(self, def_var, record_access, record):
        return record_access.extract_range(record, def_var.field, def_var.start, self.length)

    def find_category(self, dimension, value):
        return self.lookup[value] if value else self.empty

    def get_categories(self, dimension):
        return self.categories


class CnvCategory(Category):
    def __init__(self, subtotal, order, description, values):
        self.subtotal = subtotal
        self.order = order
        self.description = description
        self.values = [v for v in values if v is not None]
        self.has_empty = any(filter(lambda v: v is None or v.is_empty, values))

    def __contains__(self, value):
        for cnv_value in self.values:
            if value in cnv_value:
                return value

        return None

    def __str__(self):
        return f"{self.order} {self.description} {','.join(map(str, self.values))}"


from .parser import CnvParser
