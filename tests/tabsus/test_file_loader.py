from unittest import TestCase

from tabsus import TEST_RESOURCE_DIR
from tabsus.file_loader import *


class TestLoadFile:
    def __init__(self):
        self.loader = None

    def test_load_simple(self):
        self.assertIsNotNone(self.loader.load('rd2008.def'))
        self.assertIsNone(self.loader.load('rd2008'))

    def test_load(self):
        self.assertIsNotNone(self.loader.load('cnv/regiao.cnv'))
        self.assertIsNone(self.loader.load('cnv/noneistent.cnv'))

    def test_list_files(self):        
        self.assertEqual(4, len(self.loader.list_files('*.DEF')))
        self.assertEqual(4, len(self.loader.list_files('*.def')))
        self.assertTrue('RD2008.DEF' in self.loader.list_files('*.DEF'))
        


class TestZipFileLoader(TestCase, TestLoadFile):
    def setUp(self):
        self.loader = ZipFileLoader(os.path.join(TEST_RESOURCE_DIR, 'TAB_SIH.zip'))


class TestFileSystemLoader(TestCase, TestLoadFile):
    def setUp(self):
        self.loader = FileSystemLoader(os.path.join(TEST_RESOURCE_DIR, 'SIH'))


class TestResolvePath(TestCase):
    def test_resolve(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')

        self.assertEqual(os.path.join(sih, 'CNV/REGIAO.CNV'),
                         case_insensitive_resolve_path(sih, 'cnv/regiao.cnv'))

        self.assertTrue(os.path.exists(case_insensitive_resolve_path(sih, 'cnv/ReGiaO.cnv')))

    def test_dir_get(self):
        sih = os.path.join(TEST_RESOURCE_DIR, 'SIH')

        self.assertEqual(os.path.join(sih, 'RD2008.DEF'),
                         case_insensitive_dir_get(sih, 'rd2008.def'))

        self.assertEqual(os.path.join(sih, 'RD2008.DEF'),
                         case_insensitive_dir_get(sih, 'rd2008.DEF'))

        def_file = case_insensitive_dir_get(sih, 'Rd2008.DEF')
        self.assertTrue(os.path.exists(def_file))
