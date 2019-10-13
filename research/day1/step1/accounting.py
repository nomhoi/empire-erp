from decimal import *

DEBIT = 0
CREDIT = 1
AMOUNT = 2

class GeneralLedger(list):
    def __str__(self):
        res = '\nGeneral ledger'
        for e in self:
            res += '\n {:2} {:2} {:8.2f}'.format(e[DEBIT], e[CREDIT], e[AMOUNT])
        res += "\n----------------------"
        return res