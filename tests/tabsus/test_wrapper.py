from unittest import TestCase

import sys
import tabsus


class TestDatabase(TestCase):
    def test_parse_all_dbs(self):
        for db in tabsus.wrapper.DATABASES.values():
            tab = db.get_tabsus()
            print(tab)
            for d in tab.definitions:
                print(tab[d])

    def test_parse_ans(self):
        ans = tabsus.load_tab('ANS')

        beneficiarios = ans['DEF/tabnet_02.def']
        print(beneficiarios.dimensions)
