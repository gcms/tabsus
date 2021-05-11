import os

TEST_RESOURCE_DIR = os.path.join(os.path.dirname(__file__), '../../tests/resources')
DEFAULT_ENCODING = 'Windows-1252'

DOWNLOAD_PATH = os.environ.get('TABSUS_HOME') or os.path.join(os.environ.get('HOME'), ".local/share/tabsus/")

from .wrapper import TabSus
from .wrapper import open_def
from .wrapper import load_tab
