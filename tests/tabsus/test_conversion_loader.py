from unittest import TestCase

import tabsus
from tabsus import TEST_RESOURCE_DIR
from tabsus.conversion.cnv import CnvConversionFile
from tabsus.conversion.dbf import DbfConversionFile
from tabsus.conversion.loader import ConversionLoader
from tabsus.file_loader import *


class TestConversionLoader(TestCase):
    def test_load_file(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')

        cnv_loader = ConversionLoader(sih, tabsus.DEFAULT_ENCODING)
        cnv = cnv_loader.load('cnv/regiao.cnv')
        self.assertTrue(isinstance(cnv, CnvConversionFile))

    def test_load_file_win_path(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'TAB_SIH.zip')

        cnv_loader = ConversionLoader(sih, tabsus.DEFAULT_ENCODING)
        cnv = cnv_loader.load('cnv\\regiao.cnv')
        self.assertTrue(isinstance(cnv, CnvConversionFile))

    def test_load_zip(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'TAB_SIH.zip')

        cnv_loader = ConversionLoader(sih, tabsus.DEFAULT_ENCODING)
        cnv = cnv_loader.load('cnv/regiao.cnv')
        self.assertTrue(isinstance(cnv, CnvConversionFile))

    def test_load_dbf(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')

        cnv_loader = ConversionLoader(sih, tabsus.DEFAULT_ENCODING)
        cnv = cnv_loader.load('dbf/cid10.dbf')
        self.assertTrue(isinstance(cnv, DbfConversionFile))

        print(cnv.records)

    def test_load_dbf_zip(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'TAB_SIH.zip')

        cnv_loader = ConversionLoader(sih, tabsus.DEFAULT_ENCODING)
        cnv = cnv_loader.load('dbf/cid10.dbf')
        self.assertTrue(isinstance(cnv, DbfConversionFile))

        print(cnv.records)

    def test_load_unsupported(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'TAB_SIH.zip')

        cnv_loader = ConversionLoader(sih, tabsus.DEFAULT_ENCODING)
        with self.assertRaises(NotImplementedError):
            cnv_loader.load('Documentos/LEIAME.pdf')
