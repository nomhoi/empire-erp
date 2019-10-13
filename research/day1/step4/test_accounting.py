import pytest
from accounting import *
from decimal import *

@pytest.fixture
def accounts():
    return Accounts()

@pytest.fixture
def ledger(accounts):
    return GeneralLedger(accounts)

@pytest.fixture
def balance(accounts):
    return Balance(accounts)

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

@pytest.mark.parametrize('entries, exception', [
    ([(12, 1, 100.00)], BalanceException('BalanceException')),
    ([(12, 6, 100.00)], BalanceException('BalanceException')),
    ([(12, 11, 100.00)], BalanceException('BalanceException')),

    ([(6, 2, 100.00)], BalanceException('BalanceException')),
    #([(6, 7, 100.00)], BalanceException('BalanceException')),
    #([(6, 12, 100.00)], BalanceException('BalanceException')),

    ([(1, 2, 100.00)], BalanceException('BalanceException')),
    #([(1, 6, 100.00)], BalanceException('BalanceException')),
    #([(1, 12, 100.00)], BalanceException('BalanceException')),
])
def test_accounts_balance(accounts, ledger, entries, exception):
    for entry in entries:
        try:
            ledger.append((entry[DEBIT], entry[CREDIT], Decimal(entry[AMOUNT])))
        except BalanceException as inst:
            assert isinstance(inst, type(exception))
            assert inst.args == exception.args
        else:
            pytest.fail("Expected error but found none")

    assert len(ledger) == 0
    assert len(accounts) == 12

@pytest.mark.parametrize('entries', [
    [
        ( 1, 12, 200.00), # increase active and passive
    ],[
        ( 1, 12, 200.00), # increase active and passive
        (12,  1, 100.00), # decrease passive and decrease active
    ],[
        ( 1, 12, 300.00), # increase active and passive
        (12,  1, 100.00), # decrease passive and decrease active
        ( 2,  1, 100.00), # increase active and decrease active
    ],[
        ( 1, 12, 300.00), # increase active and passive
        (12,  1, 100.00), # decrease passive and decrease active
        ( 2,  1, 100.00), # increase active and decrease active
        (12, 11, 100.00), # decrease passive and increase passive
    ]
])
def test_balance(accounts, ledger, balance, entries):
    for entry in entries:
        ledger.append(entry)
    balance.create()
    print(ledger)
    print(accounts)
    print(balance)