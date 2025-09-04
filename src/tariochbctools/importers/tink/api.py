from typing import List, TypedDict


class ValueDict(TypedDict):
    """Represents the 'value' object inside 'amount'."""

    scale: str
    unscaledValue: str


class AmountDict(TypedDict):
    """Represents the 'amount' object."""

    currencyCode: str
    value: ValueDict


class PfmCategoryDict(TypedDict):
    """Represents the 'pfm' object inside 'categories'."""

    id: str
    name: str


class CategoriesDict(TypedDict):
    """Represents the 'categories' object."""

    pfm: PfmCategoryDict


class DatesDict(TypedDict):
    """Represents the 'dates' object."""

    booked: str
    value: str


class DescriptionsDict(TypedDict):
    """Represents the 'descriptions' object."""

    display: str
    original: str


class IdentifiersDict(TypedDict):
    """Represents the 'identifiers' object."""

    providerTransactionId: str


class MerchantInformationDict(TypedDict):
    """Represents the 'merchantInformation' object."""

    merchantCategoryCode: str
    merchantName: str


class TypesDict(TypedDict):
    """Represents the 'types' object."""

    financialInstitutionTypeCode: str
    type: str


class TransactionDict(TypedDict):
    """Represents a single transaction object in the 'transactions' list."""

    accountId: str
    amount: AmountDict
    categories: CategoriesDict
    dates: DatesDict
    descriptions: DescriptionsDict
    id: str
    identifiers: IdentifiersDict
    merchantInformation: MerchantInformationDict
    providerMutability: str
    reference: str
    status: str
    types: TypesDict


class TransactionsResponseDict(TypedDict):
    """Represents the top-level JSON response structure."""

    nextPageToken: str
    transactions: List[TransactionDict]
