from decimal import *

DEBIT = 0
CREDIT = 1
AMOUNT = 2

class BalanceException(Exception):
    pass

class Account:
    def __init__(self, id, begin=Decimal(0.00)):
        self.id = id
        self.begin = begin
        self.end = begin
        self.entries = []

    def append(self, id, amount):
        self.entries.append((id, amount))
        self.end += amount

    def is_active(self):
        return True if self.id < 5 else False

    def is_passive(self):
        return True if self.id > 8 else False

    def __str__(self):
        def dc(amount):
            if amount >= Decimal(0.00):
                debit = amount
                credit = Decimal(0.00)
            else:
                debit = Decimal(0.00)
                credit = -amount
            return "{:8.2f} {:8.2f}".format(debit, credit)

        res = ""
        if len(self.entries) > 0:
            res = "\nAccount {id} \nbeg: ".format(id=self.id)
            res += dc(self.begin)
            for account in self.entries:
                res += "\n{:3}: ".format(account[0])
                res += dc(account[1])
            res += "\nend: "
            res += dc(self.end)
            res += "\n----------------------"
        return res

class Accounts(dict):
    def __init__(self):
        self.range = range(1, 13)
        for i in self.range:
            self[i] = Account(i)

    def check_balance(self, entry):
        if self[entry[CREDIT]].end - Decimal(entry[AMOUNT]) < 0 and self[entry[CREDIT]].is_active():
            raise BalanceException('BalanceException')
        if self[entry[DEBIT]].end + Decimal(entry[AMOUNT]) > 0 and self[entry[DEBIT]].is_passive():
            raise BalanceException('BalanceException')

    def append_entry(self, entry):
        self[entry[DEBIT]].append(entry[CREDIT], Decimal(entry[AMOUNT]))
        self[entry[CREDIT]].append(entry[DEBIT], Decimal(-entry[AMOUNT]))

    def __str__(self):
        res = ""
        for i in self.range:
            res2 = self[i].__str__()
            if len(res2) > 0:
                res += res2
        return res

class GeneralLedger(list):
    def __init__(self, accounts=None):
        self.accounts = accounts

    def append(self, entry):
        if self.accounts is not None:
            self.accounts.check_balance(entry)
            self.accounts.append_entry(entry)

        super().append(entry)

    def __str__(self):
        res = '\nGeneral ledger'
        for e in self:
            res += '\n {:2} {:2} {:8.2f}'.format(e[DEBIT], e[CREDIT], e[AMOUNT])
        res += "\n----------------------"
        return res