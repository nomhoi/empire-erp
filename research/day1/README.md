# Empire ERP. Занимательная бухгалтерия: главная книга, счета, баланс.

В данной статье мы осуществим попытку проникновения в самое сердце "кровавого энтерпрайза" - в бухгалтерию. Вначале мы проведем исследование главной книги, счетов и баланса, выявим присущие им свойства и алгоритмы. Используем Python и технологию Test Driven Development. Здесь мы займемся прототипированием, поэтому вместо базы данных будем использовать базовые контейнеры: списки, словари и кортежи. Проект разрабатывается в соответствии с требованиями к проекту Empire ERP: https://github.com/nomhoi/empire-erp/blob/master/requirements.md. 

## Условие задачи

Космос... Планета Эмпирея... Одно государство на всю планету. Население работает 2 часа в 2 недели, через 2 года на пенсию. План счетов состоит из 12 позиций. Счета 1-4 - активные, 5-8  - активно-пассивные, 9-12 - пассивные. Предприятие Horns & Hooves. Все транзакции выполняются в одном отчетном периоде, в начале периода остатки отсутствуют.


## Настройка проекта

Клонируем проект с гитхаба:
```bash
git clone https://github.com/nomhoi/empire-erp.git
```

Разработку ведем на Python 3.7.4. Настраиваем виртуальное окружение, активируем его и устанавливаем __pytest__.

```bash
pip install pytest
```

## 1. Главная книга

Переходим в папку __reaserch/day1/step1__.

__accounting.py__:

```python
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
```

**test_accounting.py**:
```python
import pytest
from accounting import *
from decimal import *

@pytest.fixture
def ledger():
    return GeneralLedger()

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
```

Главная книга, как видим, представлена в виде списка записей. Каждая запись оформлена в виде кортежа. Для записи проводки пока используем только номера счетов по дебету и кредиту и сумму проводки. Даты, описания и прочая информация пока не нужны, мы их добавим позже. 

В тестовом файле создали фиксатор __ledger__ и параметризованый тест __test_ledger__. В параметр теста __entries__ передаем сразу весь список проводок. Для проверки выполняем в терминале команду __pytest -s -v__. Тест должен пройти, и мы увидим в терминале весь список транзакций сохраненных в главной книге:
```bash
General ledger
  1 12   100.00
  1 11   100.00
```

## 2. Счета

Теперь добавим в проект поддержку счетов. Переходим в папку __day1/step2__.

__accounting.py__:
```python
class GeneralLedger(list):
    def __init__(self, accounts=None):
        self.accounts = accounts

    def append(self, entry):
        if self.accounts is not None:
            self.accounts.append_entry(entry)
        super().append(entry)
```
В классе __GeneralLedger__ перегрузили метод __append__. При добавлении проводки в книгу добавляем ее сразу и в счета. 

__accounting.py__:
```python
class Account:
    def __init__(self, id, begin=Decimal(0.00)):
        self.id = id
        self.begin = begin
        self.end = begin
        self.entries = []

    def append(self, id, amount):
        self.entries.append((id, amount))
        self.end += amount

class Accounts(dict):
    def __init__(self):
        self.range = range(1, 13)
        for i in self.range:
            self[i] = Account(i)

    def append_entry(self, entry):
        self[entry[DEBIT]].append(entry[CREDIT], Decimal(entry[AMOUNT]))
        self[entry[CREDIT]].append(entry[DEBIT], Decimal(-entry[AMOUNT]))
```
Класс __Accounts__ выполнен в виде словаря. В ключах номер счета, в значениях содержимое счета, т.е. экземпляр класса __Account__, который в свою очередь содержит поля начального и конечного сальдо и список транзакций имеющих отношение к этому счету. Заметим, что в этом списке суммы проводок по дебету и кредиту хранятся в одном поле, сумма по дебету положительна, сумма по кредиту отрицательна.

**test_accounting.py**:
```python
@pytest.fixture
def accounts():
    return Accounts()

@pytest.fixture
def ledger(accounts):
    return GeneralLedger(accounts)
```
В тестовом файле добавили фиксатор __accounts__ и поправили фиксатор __ledger__.

**test_accounting.py**:
```python
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
```
Добавили новый тест __test_accounts__.

Запускаем тест и наблюдаем вывод:
```bash
General ledger
  1 12   100.00
  1 11   100.00
----------------------

Account 1
beg:     0.00     0.00
 12:   100.00     0.00
 11:   100.00     0.00
end:   200.00     0.00
----------------------
Account 11
beg:     0.00     0.00
  1:     0.00   100.00
end:     0.00   100.00
----------------------
Account 12
beg:     0.00     0.00
  1:     0.00   100.00
end:     0.00   100.00
----------------------

```
В классах __Account__ и __Acconts__ методы **\_\_str__** тоже перегружены, можно посмотреть в исходниках проекта. Суммы проводок и остатков для лучшей наглядности представлены в двух столбцах: по дебету и кредиту.

## 3. Счета: проверка проводок

Вспоминаем о таком правиле:
```bash
Остаток на активном счету может быть только по дебету.
Остаток на пассивном счету может быть только по кредиту.
Остаток на активно-пассивном счету может быть и по дебету и по кредиту.
```
То есть в экземпляре класса __Account__ значение __end__ (конечное сальдо) на активных счетах не может быть отрицательным, а на пассивных счетах не может быть положительным. 

Переходим в папку __day1/step3__.

__accounting.py__:
```python
class BalanceException(Exception):
    pass
```
Добавили исключение __BalanceException__.

```python
class Account:
    ...
    def is_active(self):
        return True if self.id < 5 else False

    def is_passive(self):
        return True if self.id > 8 else False
    ...
```
В класс __Account__ добавили проверку, к какому типу относится счет: к активному или пассивному.

```python
class Accounts(dict):
    ...
    def check_balance(self, entry):
        if self[entry[CREDIT]].end - Decimal(entry[AMOUNT]) < 0 and self[entry[CREDIT]].is_active():
            raise BalanceException('BalanceException')
        if self[entry[DEBIT]].end + Decimal(entry[AMOUNT]) > 0 and self[entry[DEBIT]].is_passive():
            raise BalanceException('BalanceException')
    ...
```
В класс __Accounts.py__ добавили проверку, если в результате добавления новой проводки на активном счету образуется отрицательное значение по дебету, то поднимется исключение, и то же самое, если на пассивном счету получится отрицательное значение по кредиту. 

```python
class GeneralLedger(list):
    ...
    def append(self, entry):
        if self.accounts is not None:
            self.accounts.check_balance(entry)
            self.accounts.append_entry(entry)

        super().append(entry)
    ...
```
В классе __GeneralLedger__ перед добавлением проводки в счета выполняем проверку. Если поднимается исключение, то проводка не попадает ни в счета, ни в главную книгу.

**test_accounting.py**:
```python
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
```
В тестовый модуль добавили тест __test_accounts_balance__. В списке проводок сначала перечислили все возможные комбинации проводок и закоммитили все проводки, которые не поднимают исключение. Запускаем тест и убеждаемся, что оставшиеся 5 вариантов проводок поднимают исключение __BalanceException__.

## 4. Баланс

Переходим в папку __day1/step4__.

__accounting.py__:
```python
class Balance(list):
    def __init__(self, accounts):
        self.accounts = accounts
        self.suma = Decimal(0.00)
        self.sump = Decimal(0.00)

    def create(self):
        self.suma = Decimal(0.00)
        self.sump = Decimal(0.00)
        for i in self.accounts.range:
            active = self.accounts[i].end if self.accounts[i].end >= 0 else Decimal(0.00)
            passive = -self.accounts[i].end if self.accounts[i].end < 0 else Decimal(0.00)
            self.append((active, passive))
            self.suma += active
            self.sump += passive
```
При создании баланса просто собираем остатки со всех счетов в одну таблицу.

**test_accounting.py**:
```python
@pytest.fixture
def balance(accounts):
    return Balance(accounts)
```
Создали фиксатор __balance__.
```python
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
    print(accounts)
    print(balance)
```

Создали тест __test_balance__. В списках параметров перечислили все возможные типы проводок: увеличивающие актив и пассив, уменьшающие актив и пассив, увеличивающие актив и уменьшающие актив, увеличивающие пассив и уменьшающие пассив. Оформили 4 варианта проводок, чтобы можно было пошагово посмотреть вывод. Для последнего варианта вывод видим такой:
```
General ledger
  1 12   300.00
 12  1   100.00
  2  1   100.00
 12 11   100.00
----------------------

Account 1
beg:     0.00     0.00
 12:   300.00     0.00
 12:     0.00   100.00
  2:     0.00   100.00
end:   100.00     0.00
----------------------
Account 2
beg:     0.00     0.00
  1:   100.00     0.00
end:   100.00     0.00
----------------------
Account 11
beg:     0.00     0.00
 12:     0.00   100.00
end:     0.00   100.00
----------------------
Account 12
beg:     0.00     0.00
  1:     0.00   300.00
  1:   100.00     0.00
 11:   100.00     0.00
end:     0.00   100.00
----------------------

Balance
 1 :   100.00     0.00
 2 :   100.00     0.00
 3 :     0.00     0.00
 4 :     0.00     0.00
 5 :     0.00     0.00
 6 :     0.00     0.00
 7 :     0.00     0.00
 8 :     0.00     0.00
 9 :     0.00     0.00
10 :     0.00     0.00
11 :     0.00   100.00
12 :     0.00   100.00
----------------------
sum:   200.00   200.00
======================
```

## 5. Сторно

Теперь проверим как выполняется сторно.

```python
@pytest.mark.parametrize('entries', [
    [
        ( 1, 12, 100.00),
        ( 1, 12,-100.00),
    ]
])
def test_storno(accounts, ledger, balance, entries):
    for entry in entries:
        ledger.append(entry)
    balance.create()
    print(ledger)
    print(accounts)
    print(balance)
```

Вывод получили такой:
```bash
General ledger
  1 12   100.00
  1 12  -100.00
----------------------

Account 1
beg:     0.00     0.00
 12:   100.00     0.00
 12:     0.00   100.00
end:     0.00     0.00
----------------------
Account 12
beg:     0.00     0.00
  1:     0.00   100.00
  1:   100.00     0.00
end:     0.00     0.00
----------------------

Balance
 1 :     0.00     0.00
 2 :     0.00     0.00
 3 :     0.00     0.00
 4 :     0.00     0.00
 5 :     0.00     0.00
 6 :     0.00     0.00
 7 :     0.00     0.00
 8 :     0.00     0.00
 9 :     0.00     0.00
10 :     0.00     0.00
11 :     0.00     0.00
12 :     0.00     0.00
----------------------
sum:     0.00     0.00
======================

```
Вроде все верно.

А если мы используем такой набор проводок, то тест пройдет:
```python
( 1, 12, 100.00),
(12,  1, 100.00),
( 1, 12,-100.00),
```

А если такой набор, поменяем последние 2 строки местами, то получим исключение:
```python
( 1, 12, 100.00),
( 1, 12,-100.00),
(12,  1, 100.00),
```
Таким образом, чтобы отловить такую ошибку сторно нужно размещать сразу после исправляемой транзакции.

## Заключение

В следующих статьях продолжим исследование бухгалтерского учета и будем рассматривать все аспекты разработки системы в соответствии с со списком требований к Empire ERP.