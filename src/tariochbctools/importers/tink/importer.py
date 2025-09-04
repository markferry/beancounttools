from datetime import date
from os import path

import beangulp
import requests
import yaml
from beancount.core import amount, data
from beancount.core.number import D

from tariochbctools.importers.general.deduplication import ReferenceDuplicatesComparator


class HttpServiceException(Exception):
    pass


class Importer(beangulp.Importer):

    API_URL = "https://api.tink.com/api/v1"
    DATA_URL = "https://api.tink.com/data/v2"

    def identify(self, filepath: str) -> bool:
        return path.basename(filepath).endswith("tink.yaml")

    def account(self, filepath: str) -> data.Entries:
        return ""

    def _configure(self, filepath: str) -> None:
        with open(filepath, "r") as f:
            config = yaml.safe_load(f)
            self.config = config

    def _get_token(self, config: dict) -> str:
        r = requests.post(
            self.API_URL + "/oauth/token",
            data={
                "client_id": config["client_id"],
                "client_secret": config["client_secret"],
                "grant_type": "authorization_code",
            },
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise HttpServiceException(e, e.response.text)

        return r.json()["access_token"]

    def _get_accounts(self, headers: dict) -> list[dict]:
        r = requests.get(
            self.DATA_URL + "/accounts",
            headers=headers,
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise HttpServiceException(e, e.response.text)

        return r.json()["accounts"]

    def _get_transactions(self, headers: dict, account_id: str) -> list[dict]:
        headers["accountIdIn"] = account_id

        r = requests.get(
            self.DATA_URL + "/transactions",
            headers=headers,
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise HttpServiceException(e, e.response.text)

        return r.json()["transactions"]

    def extract(self, filepath: str, existing: data.Entries) -> data.Entries:
        self._configure(filepath)

        token = self.config.get("access_token")
        headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        entries = []
        for account in self.config["accounts"]:
            account_id = account["id"]
            asset_account = account["asset_account"]
            transactions = self._get_transactions(headers, account_id)

            for trx in transactions:
                metakv = {}
                metakv["id"] = trx["id"]
                meta = data.new_metadata("", 0, metakv)

                trx_date = date.fromisoformat(trx["dates"]["booked"])
                narration = trx["descriptions"]["display"]
                entry = data.Transaction(
                    meta,
                    trx_date,
                    "*",
                    "",
                    narration,
                    data.EMPTY_SET,
                    data.EMPTY_SET,
                    [
                        data.Posting(
                            asset_account,
                            amount.Amount(
                                D(str(trx["amount"]["value"]["unscaledValue"])),
                                trx["amount"]["currencyCode"],
                            ),
                            None,
                            None,
                            None,
                            None,
                        ),
                    ],
                )
                entries.append(entry)

        return entries

    cmp = ReferenceDuplicatesComparator(["id"])
