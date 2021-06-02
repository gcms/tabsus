import os
import zipfile
import logging

import urllib.parse
import urllib.request
from io import TextIOWrapper

import tabsus

from tabsus.conversion.loader import ConversionLoader
from tabsus.definition.access import DefFileAccess
from tabsus.definition.parser import DefParser
from tabsus.file_loader import FileLoader


def open_def(file):
    directory = os.path.dirname(os.path.abspath(file))
    filename = os.path.basename(file)
    return TabSus(directory).load_def(filename)


class TabSus:
    def __init__(self, root, encoding=tabsus.DEFAULT_ENCODING):
        self.root = root
        self.encoding = encoding
        self.file_loader = FileLoader.open(root)
        self.cnv_loader = ConversionLoader(self.file_loader, encoding)

    def __str__(self):
        return os.path.basename(self.root)

    @property
    def definitions(self):
        return self.file_loader.list_files('*.DEF')

    def __getitem__(self, key):
        return self.load_def(key)

    def load_def(self, path):
        def_resource = self.file_loader.load(path)
        if not def_resource and not path.lower().endswith('.def'):
            def_resource = self.file_loader.load(path + '.def')

        if def_resource:
            with def_resource.open() as file:
                text = TextIOWrapper(file, self.encoding, line_buffering=True)
                parser = DefParser(text, os.path.basename(def_resource))
                definition = parser.parse()

            return DefFileAccess(definition, self.cnv_loader)

        return None


class Database:
    def __init__(self, name, tab_url):
        self.name = name
        self.tab_url = urllib.parse.urlparse(tab_url)

        self.file_path = None
        if self.tab_url.scheme == 'file':
            self.file_path = os.path.abspath(os.path.join(self.tab_url.netloc, self.tab_url.path))

    @property
    def tabsus(self):
        return self.get_tabsus()

    def get_tabsus(self):
        filename = os.path.join(tabsus.DOWNLOAD_PATH, f"{self.name}.zip")

        if not self.file_path:
            if os.path.exists(filename):
                self.file_path = os.path.abspath(filename)
            else:
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                urllib.request.urlretrieve(self.tab_url.geturl(), filename)
                self.file_path = os.path.abspath(filename)

        try:
            return TabSus(self.file_path)
        except zipfile.BadZipFile as e:
            logging.warning(f"Incomplete or invalid file {e}")
            os.remove(self.file_path)
            return self.get_tabsus()


DATABASES = [
    Database('SIH', 'ftp://ftp.datasus.gov.br/dissemin/publicos/SIHSUS/200801_/Auxiliar/TAB_SIH.zip'),
    Database('SIA', 'ftp://ftp.datasus.gov.br/dissemin/publicos/SIASUS/200801_/Auxiliar/TAB_SIA.zip'),
    Database('SIM', 'ftp://ftp.datasus.gov.br/dissemin/publicos/SIM/CID10/TAB/OBITOS_CID10_TAB.ZIP'),
    Database('SINASC', 'ftp://ftp.datasus.gov.br/dissemin/publicos/SINASC/1996_/Auxiliar/NASC_NOV_TAB.zip'),
    Database('SINANNET', 'ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/AUXILIAR/TAB_SINANNET.zip'),
    Database('SINANONLINE', 'ftp://ftp.datasus.gov.br/dissemin/publicos/SINAN/AUXILIAR/TAB_SINANONLINE.zip'),
    Database('ANS', 'http://ftp.dadosabertos.ans.gov.br/FTP/Base_de_dados/Microdados/arquivos_auxiliares_de_tab_def_e_cnv/arquivos_auxiliares_de_tabulacao.zip')
]

DATABASES = {it.name: it for it in DATABASES}


def load_tab(tabname):
    return DATABASES[tabname].get_tabsus()
