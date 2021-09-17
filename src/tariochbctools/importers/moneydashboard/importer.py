from os import path
from typing import List, NamedTuple, Optional

import yaml
from beancount.core import amount, data
from beancount.core.number import D
from beancount.ingest import importer
from moneydashboard import MoneyDashboard
from undictify import type_checked_constructor


@type_checked_constructor(skip=True, convert=True)
class MoneyDashboardTransaction(NamedTuple):
    """Transaction data from MoneyDashboard transaction API"""

    Id: str
    Description: str
    OriginalDescription: Optional[str]
    Amount: str
    Date: str
    OriginalDate: str
    IsDebit: bool
    TagId: int
    MerchantId: int
    AccountId: int
    Notes: Optional[str]
    NativeCurrency: str
    NativeAmount: str
    CurrencyExchange: Optional[str]
    AvailableCurrencyExchanges: Optional[List[str]]

    def to_beancount_transaction(self, local_account, invert_sign=False):
        tx_amount = D(self.NativeAmount)
        # avoid pylint invalid-unary-operand-type
        signed_amount = -1 * tx_amount if invert_sign else tx_amount

        metakv = {
            "mdref": self.Id,
        }

        if self.Notes:
            metakv["notes"] = self.Notes

        meta = data.new_metadata("", 0, metakv)
        # FIXME: depends on a moneydashboard patch
        date = MoneyDashboard.parse_wcf_date(self.Date).date()

        entry = data.Transaction(
            meta,
            date,
            "*",
            "",
            self.Description,
            data.EMPTY_SET,
            data.EMPTY_SET,
            [
                data.Posting(
                    local_account,
                    amount.Amount(signed_amount, self.NativeCurrency),
                    None,
                    None,
                    None,
                    None,
                ),
            ],
        )
        return entry


class Importer(importer.ImporterProtocol):
    """An importer for MoneyDashboard"""

    def __init__(self):
        self.md = None
        self.account = None
        self.existing_entries = None

    def _configure(self, file, existing_entries):
        with open(file.name, "r") as f:
            config = yaml.safe_load(f)
            self.md = MoneyDashboard(email=config["email"], password=config["password"])

        self.existing_entries = existing_entries
        self.account = config["account"]

    def identify(self, file):
        return path.basename(file.name) == "moneydashboard.yaml"

    def file_account(self, file):
        return ""

    def extract(self, file, existing_entries=None):
        self._configure(file, existing_entries)

        # FIXME: protected access
        transactions = self.md._get_transactions(2)  # since last login
        entries = []

        for trx in transactions:
            entries.extend(
                self._extract_transaction(trx, self.account, transactions, False)
            )

        return entries

    def _extract_transaction(self, trx, local_account, transactions, invert_sign):
        entries = []

        t = MoneyDashboardTransaction(**trx)
        entry = t.to_beancount_transaction(local_account, invert_sign)
        entries.append(entry)

        return entries
