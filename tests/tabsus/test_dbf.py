import os
from unittest import TestCase

from tabsus.definition import DefDimension

import tabsus
from tabsus import TEST_RESOURCE_DIR
from tabsus.conversion.loader import ConversionLoader
from tabsus.file_loader import ZipFileLoader


class TestDbfConversionFile(TestCase):
    def setUp(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'TAB_SIH.zip')
        self.loader = ConversionLoader(ZipFileLoader(sih), tabsus.DEFAULT_ENCODING)

    def test_index_case_insensitive(self):
        dbf = self.loader.load('DBF/cid10.dbf')

        index1 = dbf.get_index_by('CD_COD')
        self.assertIsNotNone(index1)
        print(index1['A000'])
        self.assertIsNotNone(index1['A000'])
        self.assertEqual('A00.0 Colera dev Vibrio cholerae 01 biot cholerae', index1['A000']['CD_DESCR'])

        index2 = dbf.get_index_by('cd_cod')
        self.assertEqual(index1, index2)

        self.assertEqual(index1, dbf.get_index_by('CD_1234'))  # undefined column, use the first one (CD_COD)
        self.assertNotEqual(index1, dbf.get_index_by('CD_DESCR'))

    def test_mapping_not_found(self):
        dbf = self.loader.load('DBF/cid10.dbf')
        self.assertIsNone(dbf.find_record('CD_COD', '1234'))
        self.assertIsNotNone(dbf.find_record('CD_COD', 'A000'))
        self.assertIsNotNone(dbf.find_record('', 'A000'))
