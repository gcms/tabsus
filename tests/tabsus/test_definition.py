import os
from unittest import TestCase

import dbfread
import pandas

import tabsus
from tabsus import TEST_RESOURCE_DIR
from tabsus import TabSus
from tabsus.definition.parser import DefParser
from tabsus.definition.access import DictionaryRecordAccess


class TestTabSus(TestCase):

    def test_def_parser(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')

        with open(os.path.join(sih, 'RD2008.DEF'), encoding=tabsus.DEFAULT_ENCODING) as file:
            rd2008 = DefParser(file).parse()
        self.assertEqual('RD2008.DEF', rd2008.name)
        self.assertEqual('Movimento de AIH - Arquivos Reduzidos', rd2008.description)
        self.assertEqual('DADOS\\RD*.DBC', rd2008.file_pattern)
        self.assertEqual('\\TAB\\RD.HLP', rd2008.help_file)

    def test_load_def(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')

        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008')
        self.assertIsNotNone(rd2008)
        self.assertEqual('RD2008.DEF', rd2008.name)
        self.assertEqual('Movimento de AIH - Arquivos Reduzidos', rd2008.description)
        self.assertEqual('RD2008.DEF - Movimento de AIH - Arquivos Reduzidos', str(rd2008))

    def test_load_def_zip(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'TAB_SIH.zip')
        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008')
        self.assertIsNotNone(rd2008)

    def test_def_vars(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008.def')

        self.assertIsNotNone(rd2008['Ano de internação'])
        self.assertEqual('Ano de internação', rd2008['Ano de internação'].name)
        self.assertEqual('DT_INTER', rd2008['Ano de internação'].field)

        self.assertEqual('Valor Total', rd2008.increments['Valor Total'].name)
        self.assertEqual('VAL_TOT', rd2008.increments['Valor Total'].field)

    def test_categories(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008.def')

        ano_int = rd2008.rows['Ano de internação']
        print(ano_int)

        self.assertTrue('2021' in ano_int.values)
        self.assertFalse('1980' in ano_int.values)

        grupo_proc = rd2008['Grupo de Procedimentos']
        print(grupo_proc.values)
        self.assertTrue('Procedimentos com finalidade diagnóstica' in grupo_proc.values)
        self.assertTrue('Ações de promoção e prevenção em saúde' in grupo_proc.values)

    def test_simple_mapping(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008.def')

        record = {'DT_INTER': '20210105', 'MUNIC_RES': '520870', 'PROC_REA': '0303040092', 'VAL_TOT': 100.92}
        rd2008.record_access = DictionaryRecordAccess(record)

        self.assertEqual('5 Região Centro-Oeste', rd2008.transform('Região de Residência', record))
        self.assertEqual('TRATAMENTO CONSERVADOR DE TRAUMATISMO CRANIOENCEFÁLICO (GRAU MÉDIO)',
                         rd2008.transform('Procedimentos realizados', record))

        self.assertEqual('2021', rd2008.transform('Ano de internação', record))
        self.assertEqual(100.92, rd2008.transform('Valor Total', record))

    def test_simple_mapping_accessor(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008.def')

        record = {'DT_INTER': '20210105', 'MUNIC_RES': '520870', 'PROC_REA': '0303040092', 'VAL_TOT': 100.92}

        regiao = rd2008['Região de Residência']
        valor_total = rd2008['Valor Total']
        self.assertEqual('5 Região Centro-Oeste', regiao(record))
        self.assertEqual(100.92, valor_total(record))

    def test_mapping_long_field(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)
        rd2008 = sih.load_def('rd2008.def')

        record = {'DT_INTER': '20210105', 'MUNIC_RES': '520870', 'PROC_REA': '0303040092', 'VAL_TOT': 100.92,
                  'COD_IDADE': '2', 'IDADE': '21'}
        rd2008.record_access = DictionaryRecordAccess(record)

        self.assertEqual('21 dias', rd2008['Idade detalhada'](record))

    def test_mapping_empty_value(self):
        sinan = tabsus.load_tab('SINANNET')
        dengue = sinan['InfluenzaNET.def']
        # dengue.record_access = DictionaryRecordAccess(record)

        result = dengue.rows['Resultado Cultura']
        self.assertEqual('Ign/Branco', result({'CULT_RES': ''}))
        self.assertEqual('Ign/Branco', result({'CULT_RES': ' '}))

    def test_accessor_cnv_loader(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')
        sih = TabSus(sih)

        rd2008 = sih.load_def('rd2008.def')

        self.assertEqual(rd2008.columns['Ano/Mês internação'].cnv_filename,
                         rd2008.selections['Ano/Mês internação'].cnv_filename)

        rd2008.get_cnv(rd2008.columns['Ano/Mês internação'])
        self.assertEqual(1, len(rd2008.cnv_loader.cnv_files))

        rd2008.get_cnv(rd2008.selections['Ano/Mês internação'])
        self.assertEqual(1, len(rd2008.cnv_loader.cnv_files))

        self.assertNotEqual(rd2008.columns['Ano/Mês internação'].cnv_filename,
                            rd2008.rows['Ano/Mês internação'].cnv_filename)
        rd2008.get_cnv(rd2008.rows['Ano/Mês internação'])
        self.assertEqual(2, len(rd2008.cnv_loader.cnv_files))
