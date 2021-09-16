from os import path

import yaml
from beancount.ingest import importer
from moneydashboard import MoneyDashboard


class Importer(importer.ImporterProtocol):
    """An importer for MoneyDashboard unofficial API"""

    def __init__(self):
        self.md = None
        pass

    def _configure(self, file, existing_entries):
        with open(file.name, "r") as f:
            config = yaml.safe_load(f)
            self.md = MoneyDashboard(email=config["email"], password=config["password"])

    def identify(self, file):
        return "moneydashboard.yaml" == path.basename(file.name)

    def file_account(self, file):
        return ""

    def extract(self, file, existing_entries=None):
        self._configure(file, existing_entries)

        entries = []
        return entries
