import os.path
from unittest import TestCase

import tabsus
from tabsus.conversion.cnv import CnvParser


class TestCnvParser(TestCase):
    def setUp(self):
        self.cnv_dir = os.path.join(tabsus.TEST_RESOURCE_DIR, 'SIH/CNV')

    def test_parse(self):
        leitos = os.path.join(self.cnv_dir, 'LEITOS.CNV')

        parser = CnvParser(open(leitos, encoding=tabsus.DEFAULT_ENCODING))
        cnv = parser.parse()
        self.assertIsNotNone(cnv)

    def test_parse_all(self):
        for cnv_file in os.listdir(self.cnv_dir):
            if cnv_file.lower().endswith('cnv'):
                print(cnv_file)
                with open(os.path.join(self.cnv_dir, cnv_file), encoding=tabsus.DEFAULT_ENCODING) as file:
                    parser = CnvParser(file)
                    cnv = parser.parse()
                self.assertIsNotNone(cnv)

    def test_mapping(self):
        anov1 = os.path.join(self.cnv_dir, 'ANOv1.CNV')
        with open(anov1, encoding=tabsus.DEFAULT_ENCODING) as file:
            parser = CnvParser(file)
            cnvv1 = parser.parse()
        self.assertEqual('2021', cnvv1.lookup['21'].description)

        anov2 = os.path.join(self.cnv_dir, 'ANOv2.CNV')
        with open(anov2, encoding=tabsus.DEFAULT_ENCODING) as file:
            parser = CnvParser(file)
            cnvv2 = parser.parse()

        self.assertEqual('Ign/outros', cnvv2.lookup['21'].description)

        saida = os.path.join(self.cnv_dir, 'SAIDAPERMc.CNV')
        with open(saida, encoding=tabsus.DEFAULT_ENCODING) as file:
            parser = CnvParser(file)
            cnv = parser.parse()

        # it looks like an error in the example CNV file, but compatible with tabwin behavior
        self.assertEqual('Alta mãe/alta RN', cnv.lookup['43'].description)
        self.assertEqual('Alta mãe/alta RN', cnv.lookup['61'].description)
        self.assertEqual('Alta mãe/alta RN', cnv.lookup['17'].description)

    def test_range_type(self):
        perm = os.path.join(self.cnv_dir, 'PERM.CNV')

        with open(perm, encoding=tabsus.DEFAULT_ENCODING) as file:
            parser = CnvParser(file)
            cnv = parser.parse()

        self.assertEqual('8-14 dias', cnv.lookup['0008'].description)
        self.assertEqual('8-14 dias', cnv.lookup['0009'].description)
        self.assertEqual('8-14 dias', cnv.lookup['0014'].description)

        self.assertEqual('29 dias e +', cnv.lookup['0029'].description)
        self.assertEqual('29 dias e +', cnv.lookup['0030'].description)
        self.assertEqual('29 dias e +', cnv.lookup['0050'].description)

    def test_range_values(self):
        path = os.path.join(self.cnv_dir, 'CIDX11.CNV')

        with open(path, encoding=tabsus.DEFAULT_ENCODING) as file:
            parser = CnvParser(file)
            cnv = parser.parse()

        self.assertIsNotNone(cnv.lookup['K012'])
        self.assertIsNone(cnv.lookup['ABCD'])
        self.assertEqual('K01   Dentes inclusos e impactados', cnv.lookup['K011'].description)
        self.assertEqual('K01   Dentes inclusos e impactados', cnv.lookup['K012'].description)
        self.assertEqual('K01   Dentes inclusos e impactados', cnv.lookup['K019'].description)
