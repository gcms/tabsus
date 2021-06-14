from tabsus.conversion import RecordAccess
from tabsus.definition import DefDimension, DefFileContext


class DefVariableAccess:
    def __init__(self, def_access, def_var):
        self.def_access = def_access
        self.def_var = def_var

    def __getattr__(self, attr):
        return getattr(self.def_var, attr)

    def __str__(self):
        return str(self.def_var)

    def __repr__(self):
        return self.def_var.name

    def __call__(self, *args, **kwargs):
        return self.transform(args[0])

    def transform(self, record):
        return self.def_access.transform(self.def_var, record)

    def map(self, value):
        return self.def_access.map(self.def_var, value)

    @property
    def values(self):
        return self.def_access.get_values(self.def_var)

    @property
    def mapping(self):
        return self.def_var.get_mapping(self.def_access)


class DefVariableList(list):
    def __init__(self, variables):
        list.__init__(self, variables)
        self.variables = {v.name: v for v in variables}

    def __str__(self):
        return f"[{', '.join(map(lambda x: x.name, self))}]"

    def __repr__(self):
        return str(self)

    def __getitem__(self, key):
        return self.variables[key]

    def __contains__(self, key):
        return self.variables.get(key)


class SimpleRecordAccess(RecordAccess):
    def extract_range(self, record, field_name, start, length):
        return record[field_name][start:start + length]

    def extract_field(self, record, field_name):
        return record[field_name]

    def map(self, value, func):
        return func(value)


class DictionaryRecordAccess(RecordAccess):
    def __init__(self, schema):
        if isinstance(schema, dict):
            schema = list(schema.keys())

        self.schema = schema
        self.indexes = {self.schema[i]: i for i in range(len(self.schema))}

    def extract_range(self, record, field_name, start, length):
        result = ''

        field_index = self.indexes[field_name]
        while len(result) < start + length and field_index < len(self.indexes):
            result += record[self.schema[field_index]]
            field_index += 1

        return result[start:start + length]

    def extract_field(self, record, field_name):
        return record[field_name]

    def map(self, value, func):
        return func(value)


class DefFileAccess(DefFileContext):
    def __init__(self, def_file, cnv_loader, schema=None):
        super().__init__(def_file, cnv_loader, DefFileAccess._get_record_access(schema))
        # self.def_file = def_file
        # self.cnv_loader = cnv_loader
        self.variables = [DefVariableAccess(self, v) for v in def_file.variables]

        # self.record_access = None
        # self.set_schema(schema)

    @staticmethod
    def _get_record_access(schema):
        if isinstance(schema, dict):
            schema = list(schema.keys())

        if isinstance(schema, list):
            return DictionaryRecordAccess(schema)
        else:
            return SimpleRecordAccess()

    def __getattr__(self, attr):
        return getattr(self.def_file, attr)

    # def get_cnv(self, var):
    #     return self.cnv_loader.get(var.cnv_filename)

    def __getitem__(self, item):
        var = self.get_variable(item)
        if not var:
            raise KeyError(
                f"Variable '{item}' not available in '{self.name}.\nTry one of {self.variables}")

        return var

    def __contains__(self, item):
        return self.get_variable(item)

    def __repr__(self):
        return repr(self.def_file)

    def __str__(self):
        return str(self.def_file)

    def get_variable(self, name):
        for v in self.variables:
            if v.def_var.name == name:
                return v

        return None

    def _get_variables(self, filter_func):
        if not hasattr(filter_func, '__call__'):
            var_type = filter_func

            def filter_func(v):
                return v.var_type == var_type or v.var_type in var_type

        return DefVariableList([v for v in self.variables if filter_func(v.def_var)])

    @property
    def dimensions(self):
        return self._get_variables(lambda v: v.var_type != 'I')

    @property
    def increments(self):
        return self._get_variables(['I', 'E'])

    @property
    def rows(self):
        return self._get_variables(['L', 'X', 'D', 'T'])

    @property
    def columns(self):
        return self._get_variables(['C', 'X', 'D', 'T'])

    @property
    def selections(self):
        return self._get_variables('S')

    def _get_def_var(self, variable):
        if isinstance(variable, str):
            variable = self.get_variable(variable)

        if isinstance(variable, DefVariableAccess):
            variable = variable.def_var

        return variable

    def extract(self, record, field, length):
        return self.record_access.extract(record, field, length)

    def transform(self, variable, record):
        return self._get_def_var(variable).transform(self, record)

    def map(self, variable, value):
        return self._get_def_var(variable).map(self, value)

    def get_values(self, variable):
        if isinstance(variable, DefVariableAccess):
            variable = variable.def_var

        if not isinstance(variable, DefDimension):
            raise ValueError("Values are available only for dimensions")

        cnv = self.get_cnv(variable)
        return [c.description for c in cnv.get_categories(variable)]
