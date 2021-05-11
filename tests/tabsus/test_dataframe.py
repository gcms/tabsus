import os
from unittest import TestCase

import dbfread
import pandas

import tabsus
from tabsus import TEST_RESOURCE_DIR
from tabsus import TabSus
from tabsus.dataframe import DataFrameWrapper


class TestDataFrameAccess(TestCase):
    def test_mapping_year(self):
        sih = os.path.join(tabsus.TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)

        dbf = dbfread.DBF(os.path.join(TEST_RESOURCE_DIR, 'teste.dbf'), encoding='Windows-1252')
        df = pandas.DataFrame(dbf)
        df = df[df['DT_INTER'] < '20210000']

        rd2008 = DataFrameWrapper(sih.load_def('rd2008.def'), df)

        self.assertTrue(df['DT_INTER'].str[0:4].equals(rd2008['Ano de internação']))

    def test_mapping_sexo(self):
        sih = os.path.join(tabsus.TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008.def')

        dbf = dbfread.DBF(os.path.join(TEST_RESOURCE_DIR, 'teste.dbf'), encoding='Windows-1252')
        df = pandas.DataFrame(dbf)
        rdtab = df.tabsus(rd2008)

        for a, b in zip(df['SEXO'].str[0:6].items(), rdtab['Sexo'].items()):
            a, b = a[1], b[1]
            print(f"{a} => {b}")
            self.assertTrue(b == 'Feminino' or a not in ['2', '3'])
            self.assertTrue(b == 'Masculino' or a != '1')
            self.assertTrue(b == 'Ignorado' or a in ['1', '2', '3'])

    def test_mapping_idade(self):
        sih = os.path.join(tabsus.TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008.def')

        dbf = dbfread.DBF(os.path.join(TEST_RESOURCE_DIR, 'teste.dbf'), encoding='Windows-1252')
        df = pandas.DataFrame(dbf)
        rdtab = df.tabsus(rd2008)

        print(rdtab['Idade detalhada'])
