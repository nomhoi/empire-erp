import pytest
from accounting import *
from decimal import *

@pytest.fixture
def accounts():
    return Accounts()

@pytest.fixture
def ledger(accounts):
    return GeneralLedger(accounts)

@pytest.mark.parametrize('entries', [
    [(1, 12, 100.00),
     (1, 11, 100.00)]
])
def test_ledger(ledger, entries):
    for entry in entries:
        ledger.append((entry[DEBIT], entry[CREDIT], Decimal(entry[AMOUNT])))
    assert len(ledger) == 2
    assert ledger[0][DEBIT] == 1
    assert ledger[0][CREDIT] == 12
    assert ledger[0][AMOUNT] == Decimal(100.00)
    assert ledger[1][DEBIT] == 1
    assert ledger[1][CREDIT] == 11
    assert ledger[1][AMOUNT] == Decimal(100.00)
    print(ledger)

@pytest.mark.parametrize('entries', [
    [(1, 12, 100.00),
     (1, 11, 100.00)]
])
def test_accounts(accounts, ledger, entries):
    for entry in entries:
        ledger.append((entry[DEBIT], entry[CREDIT], Decimal(entry[AMOUNT])))
    assert len(ledger) == 2
    assert ledger[0][DEBIT] == 1
    assert ledger[0][CREDIT] == 12
    assert ledger[0][AMOUNT] == Decimal(100.00)
    assert len(accounts) == 12
    assert accounts[1].end == Decimal(200.00)
    assert accounts[11].end == Decimal(-100.00)
    assert accounts[12].end == Decimal(-100.00)
    print(ledger)
    print(accounts)