import pandas

from tabsus.definition import DefFileContext
from tabsus.definition.access import DefVariableList, RecordAccess


@pandas.api.extensions.register_dataframe_accessor("tabsus")
class TabSusAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

    def __call__(self, *args, **kwargs):
        return DataFrameWrapper(args[0], self._obj)


class DataFrameWrapper:
    def __init__(self, def_access, df):
        self.def_access = DataFrameAccess(def_access, df)
        self.df = df

    def __getattr__(self, name):
        if hasattr(self.def_access, name):
            return getattr(self.def_access, name)
        else:
            return getattr(self.df, name)

    def __getitem__(self, key):
        if key in self.def_access:
            return self.def_access[key].transform(self.df)
        else:
            return self.df.__getitem__(key)

    def _get_variables(self, vars):
        return DefVariableListWrapper(self.df, [DataFrameVariableAccess(self, v) for v in vars])

    @property
    def columns(self):
        return self._get_variables(self.def_access.columns)

    @property
    def rows(self):
        return self._get_variables(self.def_access.rows)

    @property
    def selections(self):
        return self._get_variables(self.def_access.selections)

    @property
    def increments(self):
        return self._get_variables(self.def_access.increments)


class DefVariableListWrapper:
    def __init__(self, df, variables):
        self.df = df
        self.variables = {var.name: var for var in variables}

    def __getitem__(self, item):
        var = self.variables[item]
        return var.transform(self.df)


class DataFrameVariableWrapper:
    def __init__(self, def_var_access, df):
        self.def_var_access = def_var_access
        self.df = df


class DataFrameRecordAccess(RecordAccess):
    def __init__(self, schema):
        self.schema = schema
        self.indexes = {schema[i]: i for i in range(len(schema))}

    def extract_range(self, dataframe, field_name, start, length):
        result = dataframe[field_name]

        field_index = self.indexes[field_name] + 1
        cur_len = result.str.len().max()
        while cur_len < start + length and field_index < len(self.indexes):
            next_series = dataframe[self.schema[field_index]]
            # TODO: find a better way to handle these rare cases where the following field is not string
            if next_series.dtype != object:
                fmt = "{:0>" + f"{(length - (cur_len - start))}" + "}"
                next_series = next_series.map(fmt.format)

            result = result + next_series
            field_index += 1
            cur_len = result.str.len().max()

        return result.str[start:start + length]

    def extract_field(self, dataframe, field_name):
        return dataframe[field_name]

    def map(self, series, fn):
        return series.apply(fn)


class DataFrameVariableAccess:
    def __init__(self, def_access, def_var_access):
        self.def_access = def_access
        self.def_var = def_var_access.def_var

    def __call__(self, *args, **kwargs):
        return self.transform(args[0])

    def transform(self, obj):
        if isinstance(obj, pandas.DataFrame):
            return self.def_var.transform(self.def_access, obj)
        elif isinstance(obj, pandas.Series):
            return obj.apply(self.def_var.map)
        else:
            return self.def_var.transform(obj)

    def __getattr__(self, attr):
        return getattr(self.def_var, attr)

    def __repr__(self):
        return self.def_var.name

    def __str__(self):
        return str(self.def_var)


class DataFrameAccess(DefFileContext):
    def __init__(self, def_access, schema):
        self.def_access = def_access
        if isinstance(schema, pandas.DataFrame):
            schema = schema.columns

        super().__init__(def_access.def_file, def_access.cnv_loader, DataFrameRecordAccess(schema))

    def _get_variables(self, vars):
        return DefVariableList([DataFrameVariableAccess(self, v) for v in vars])

    @property
    def columns(self):
        return self._get_variables(self.def_access.columns)

    @property
    def rows(self):
        return self._get_variables(self.def_access.rows)

    @property
    def selections(self):
        return self._get_variables(self.def_access.selections)

    @property
    def increments(self):
        return self._get_variables(self.def_access.increments)

    def __getitem__(self, item):
        return DataFrameVariableAccess(self, self.def_access[item])

    def __contains__(self, item):
        return item in self.def_access

    def transform(self, variable, df):
        return variable.def_var.extract(self, record)

    def get_cnv(self, cnv_filename):
        return self.def_access.get_cnv(cnv_filename)
