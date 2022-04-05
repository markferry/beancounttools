import json

import pytest
from beancount.core import data
from beancount.ingest import cache

from tariochbctools.importers.moneydashboard import importer as mdimp

# pylint: disable=protected-access

TEST_CONFIG = b"""
    email: something@somewhere.com
    password: some-password
    account: Some:Account
    all_transactions: false
"""

TEST_TRX = """
{
    "Id": 754837318,
    "Description": "WILLCROP LTD",
    "OriginalDescription": "WILLCROP LTD",
    "Amount": -15.35,
    "Date": "/Date(1631664000000)/",
    "OriginalDate": "/Date(-62135596800000)/",
    "IsDebit": true,
    "TagId": -1,
    "MerchantId": 194632,
    "AccountId": 1666071,
    "Notes": null,
    "NativeCurrency": "GBP",
    "NativeAmount": -15.35,
    "CurrencyExchange": null,
    "AvailableCurrencyExchanges": []
}
"""


@pytest.fixture(name="tmp_config")
def tmp_config_fixture(tmp_path):
    config = tmp_path / "moneydashboard.yaml"
    config.write_bytes(TEST_CONFIG)
    yield cache.get_file(config)  # a FileMemo, not a Path


@pytest.fixture(name="importer")
def moneydashboard_importer_fixture(tmp_config, mocker):
    mocker.patch("moneydashboard.MoneyDashboard._get_accounts", return_value=[])
    importer = mdimp.Importer()
    importer._configure(tmp_config, [])
    yield importer


@pytest.fixture(name="tmp_trx")
def tmp_trx_fixture():
    yield json.loads(TEST_TRX)


def test_identify(importer, tmp_config):
    assert importer.identify(tmp_config)


def test_extract_transaction_simple(importer, tmp_trx):
    entries = importer._extract_transaction(
        tmp_trx, importer.account, [tmp_trx], invert_sign=False
    )
    data.sanity_check_types(entries[0])
