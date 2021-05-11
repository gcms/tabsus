class CnvArrayIndex:
    def __init__(self, cnv):
        self.values = [None for _ in range(10 ** cnv.length + 1)]

        for category in cnv.categories:
            for value in category.values:
                self.values[int(value.value)] = category

    def __getitem__(self, value):
        if not value.isdigit():
            return None

        index = int(value)
        return self.values[index] if index < len(self.values) else None


class CnvHashIndex:
    def __init__(self, cnv):
        self.values = {}

        for category in cnv.categories:
            for value in category.values:
                self.values[value.value] = category

    def __getitem__(self, value):
        return self.values.get(value)


from intervaltree import IntervalTree


class CnvRangeTree:
    def __init__(self, cnv):
        self.tree = IntervalTree()
        self.categories = cnv.categories
        self.categories.sort(key=(lambda it: -int(it.order)))

        for category in self.categories:
            for value in category.values:
                self.tree[value] = category

    def __getitem__(self, value):
        interval = sorted(self.tree[value], key=lambda it: int(it.data.order))
        return interval[0].data if len(interval) > 0 else None


class CnvLinearLookup:
    def __init__(self, cnv):
        self.categories = list(cnv.categories)
        self.categories.sort(key=(lambda it: int(it.order)))

    def __getitem__(self, value):
        for category in self.categories:
            if value in category:
                return category

        return None


from decimal import Decimal


class CnvBinarySearchRange:
    def __init__(self, cnv):
        def get_single_value(category):
            assert len(category.values) == 1 and category.values[0].is_single_valued
            return Decimal(category.values[0].value)

        self.categories = cnv.categories
        self.values = [get_single_value(c) for c in self.categories]

    def __getitem__(self, value):
        numeric_value = Decimal(value)
        index = self.binary_search(numeric_value)
        return self.categories[index]

    def binary_search(self, value):
        result = -1

        start = 0
        end = len(self.values) - 1

        while end >= start:
            middle = int(start + (end - start) / 2)
            result = middle

            if value == self.values[middle]:
                break
            elif value < self.values[middle]:
                end = middle
                if end == start:
                    break
            else:
                start = middle + 1

        return result
