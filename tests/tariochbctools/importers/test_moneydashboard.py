import pytest
from beancount.ingest import cache

from tariochbctools.importers.moneydashboard import importer as mdimp

# pylint: disable=protected-access

TEST_CONFIG = b"""
    email: something@somewhere.com
    password: some-password
"""


@pytest.fixture(name="tmp_config")
def tmp_config_fixture(tmp_path):
    config = tmp_path / "moneydashboard.yaml"
    config.write_bytes(TEST_CONFIG)
    yield cache.get_file(config)  # a FileMemo, not a Path


@pytest.fixture(name="importer")
def moneydashboard_importer_fixture(tmp_config):
    importer = mdimp.Importer()
    importer._configure(tmp_config, [])
    yield importer


def test_identify(importer, tmp_config):
    assert importer.identify(tmp_config)
