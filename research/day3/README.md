# Empire ERP. Занимательная бухгалтерия: Аналитический учет


## Настройка проекта

Клонируем проект с гитхаба:
```bash
git clone https://github.com/nomhoi/empire-erp.git
```

Заходим в папку **reaserch/day3/**.

Запустим базу данных и выполним тесты:

```bash
docker-compose run test
```

Подключимся к базе данных **empire-erp**:
```bash
docker exec -it db psql -U postgres -d empire-erp
```

## Step 1. Простые счета

Счета без субсчетов называются простыми счетами. На этом шаге повторим получение оборотов по счетам с использованием главной книги.

Выполним команду в командной строке **psql** для инициализации базы данных:
```
empire-erp=# \i step1.sql
```

Файл **step1.sql**:
```sql
DROP TABLE IF EXISTS general_journal;

CREATE TABLE general_journal(
    id        serial,
    debit_id  smallint NOT NULL,
    credit_id smallint NOT NULL,
    amount    money NOT NULL
);
```

Создаем журнал проводок **general journal**. В прошлой статье ошибка, на самом деле это журнал проводок, а не главная книга.

Заполняем журнал проводок какими-нибудь исходными данными:
```sql
INSERT INTO general_journal(debit_id, credit_id, amount)
VALUES  (1, 12, 100.00),
        (1, 6, 120.00),
        (12, 1, 20.00);
INSERT 0 3
```
Выводим содержимое журнала:
```sql
SELECT      *
FROM        general_journal
ORDER BY    id;
 id | debit_id | credit_id | amount  
----+----------+-----------+---------
  1 |        1 |        12 | $100.00
  2 |        1 |         6 | $120.00
  3 |       12 |         1 |  $20.00
(3 rows)

```
Получаем из журнала проводок главную книгу и сохраняем ее в таблице **general_ledger**:
```sql
DROP TABLE IF EXISTS general_ledger;

SELECT id                AS general_journal_id,
       debit_id          AS account_id,
       credit_id         AS corresp_id,
       amount            AS debit_amount,
       ( 0.00 ) :: money AS credit_amount
INTO general_ledger
FROM general_journal
UNION
SELECT id                AS general_journal_id,
       credit_id         AS account_id,
       debit_id          AS corresp_id,
       ( 0.00 ) :: money AS debit_amount,
       amount            AS credit_amount
FROM general_journal
ORDER BY general_journal_id;
DROP TABLE
SELECT 6
```
Выводим содержимое главной книги:
```sql
SELECT      *
FROM        general_ledger
ORDER BY    general_journal_id;
 general_journal_id | account_id | corresp_id | debit_amount | credit_amount 
--------------------+------------+------------+--------------+---------------
                  1 |          1 |         12 |      $100.00 |         $0.00
                  1 |         12 |          1 |        $0.00 |       $100.00
                  2 |          1 |          6 |      $120.00 |         $0.00
                  2 |          6 |          1 |        $0.00 |       $120.00
                  3 |          1 |         12 |        $0.00 |        $20.00
                  3 |         12 |          1 |       $20.00 |         $0.00
(6 rows)

```
Обороты по счетам:
```sql
SELECT      account_id,
            sum(debit_amount)   AS debit_turnout,
            sum(credit_amount)  AS credit_turnout
FROM        general_ledger
GROUP BY    account_id
ORDER BY    account_id;
 account_id | debit_turnout | credit_turnout 
------------+---------------+----------------
          1 |       $220.00 |         $20.00
          6 |         $0.00 |        $120.00
         12 |        $20.00 |        $100.00
(3 rows)

```


## Step 2. Сложные счета

Cчета с субсчетами называются сложными счетами. Напомню, что по нашим условиям счета 1-4 являются активными, 5-8 - активно-пассивными и 9-12 - пассивными. Введем дополнительное условие: каждый четный счет является сложным счетом.

Файл **step2.sql**. Создаем журнал проводок **general journal** содержащий субсчета:
```sql
DROP TABLE IF EXISTS general_journal;

CREATE TABLE general_journal(
    id              serial,
    debit_id        smallint NOT NULL,
    debit_sub_id    smallint,
    credit_id       smallint NOT NULL,
    credit_sub_id   smallint,
    amount          money NOT NULL
);
```

Заполняем журнал проводок какими-нибудь исходными данными:
```sql
INSERT INTO general_journal(debit_id, debit_sub_id, credit_id, credit_sub_id, amount)
VALUES  ( 1, NULL, 12,    1, 100.00),
        ( 1, NULL, 12,    2, 140.00),
        ( 1, NULL,  6,    1, 120.00),
        ( 6,    2,  1, NULL,  80.00),
        (12,    1,  1, NULL,  20.00),
        (12,    2,  1, NULL,  40.00);

INSERT 0 6
```
Здесь мы должны помнить, что в сложных счетах субсчет не может принимать значение NULL, а в простых счетах значение субсчета всегда должно быть равным NULL . Можно, например, добавить триггер, который будет проверять этот момент.

Выводим содержимое журнала:
```sql
SELECT      *
FROM        general_journal
ORDER BY    id;
 id | debit_id | debit_sub_id | credit_id | credit_sub_id | amount  
----+----------+--------------+-----------+---------------+---------
  1 |        1 |              |        12 |             1 | $100.00
  2 |        1 |              |        12 |             2 | $140.00
  3 |        1 |              |         6 |             1 | $120.00
  4 |        6 |            2 |         1 |               |  $80.00
  5 |       12 |            1 |         1 |               |  $20.00
  6 |       12 |            2 |         1 |               |  $40.00
(6 rows)

```
Получаем из журнала проводок главную книгу и сохраняем ее в таблице **general_ledger**:
```sql
DROP TABLE IF EXISTS general_ledger;

SELECT id                AS gj_id,
       debit_id          AS acc_id,
       debit_sub_id      AS acc_sub_id,
       credit_id         AS cor_id,
       credit_sub_id     AS cor_sub_id,
       amount            AS debit_amount,
       ( 0.00 ) :: money AS credit_amount
INTO general_ledger
FROM general_journal
UNION
SELECT id                AS gj_id,
       credit_id         AS acc_id,
       credit_sub_id     AS acc_sub_id,
       debit_id          AS cor_id,
       debit_sub_id      AS cor_sub_id,
       ( 0.00 ) :: money AS debit_amount,
       amount            AS credit_amount
FROM general_journal
ORDER BY gj_id;
DROP TABLE
SELECT 12
```
Выводим содержимое главной книги:
```sql
SELECT      *
FROM        general_ledger
ORDER BY    gj_id;
 gj_id | acc_id | acc_sub_id | cor_id | cor_sub_id | debit_amount | credit_amount 
-------+--------+------------+--------+------------+--------------+---------------
     1 |      1 |            |     12 |          1 |      $100.00 |         $0.00
     1 |     12 |          1 |      1 |            |        $0.00 |       $100.00
     2 |      1 |            |     12 |          2 |      $140.00 |         $0.00
     2 |     12 |          2 |      1 |            |        $0.00 |       $140.00
     3 |      1 |            |      6 |          1 |      $120.00 |         $0.00
     3 |      6 |          1 |      1 |            |        $0.00 |       $120.00
     4 |      1 |            |      6 |          2 |        $0.00 |        $80.00
     4 |      6 |          2 |      1 |            |       $80.00 |         $0.00
     5 |      1 |            |     12 |          1 |        $0.00 |        $20.00
     5 |     12 |          1 |      1 |            |       $20.00 |         $0.00
     6 |      1 |            |     12 |          2 |        $0.00 |        $40.00
     6 |     12 |          2 |      1 |            |       $40.00 |         $0.00
(12 rows)

```
Обороты по синтетическим счетам:
```sql
SELECT      acc_id,
            sum(debit_amount)   AS debit_turnout,
            sum(credit_amount)  AS credit_turnout
FROM        general_ledger
GROUP BY    acc_id
ORDER BY    acc_id;
 acc_id | debit_turnout | credit_turnout 
--------+---------------+----------------
      1 |       $360.00 |        $140.00
      6 |        $80.00 |        $120.00
     12 |        $60.00 |        $240.00
(3 rows)

```
Обороты по субсчетам:
```sql
SELECT      acc_id,
            acc_sub_id,
            sum(debit_amount)   AS debit_turnout,
            sum(credit_amount)  AS credit_turnout
FROM        general_ledger
GROUP BY    acc_id, acc_sub_id
ORDER BY    acc_id, acc_sub_id;
 acc_id | acc_sub_id | debit_turnout | credit_turnout 
--------+------------+---------------+----------------
      1 |            |       $360.00 |        $140.00
      6 |          1 |         $0.00 |        $120.00
      6 |          2 |        $80.00 |          $0.00
     12 |          1 |        $20.00 |        $100.00
     12 |          2 |        $40.00 |        $140.00
(5 rows)

```

## Step 3. Счет материалы. Синтетический учет

Сейчас ненадолго вернемся на Землю, в Россию. Будем манипулировать объектами, которые можно увидеть и потрогать. Используем счет 10 "Материалы".

Файл **step3.sql**:
```sql
DROP TABLE IF EXISTS general_journal;

CREATE TABLE general_journal(
    id              serial,
    debit_id        smallint NOT NULL,
    credit_id       smallint NOT NULL,
    amount          money NOT NULL
);
```
Выполняем проводки с использованием счета 10:
```sql
INSERT INTO general_journal(debit_id, credit_id, amount)
VALUES  (10, 60, 400.00),
        (19, 60,  72.00),
        (20, 10,  50.00);
INSERT 0 3
```
Первой проводкой получаем какие-то материалы от поставщика. Второй проводкой начисляем НДС.
Третьей проводкой отпускаем материалы в производство.

Выводим содержимое журнала:
```sql
SELECT      *
FROM        general_journal
ORDER BY    id;
 id | debit_id | credit_id | amount  
----+----------+-----------+---------
  1 |       10 |        60 | $400.00
  2 |       19 |        60 |  $72.00
  3 |       20 |        10 |  $50.00
(3 rows)

```
Получаем из журнала проводок главную книгу и сохраняем ее в таблице **general_ledger**:
```sql
DROP TABLE IF EXISTS general_ledger;

SELECT id                AS gj_id,
       debit_id          AS account_id,
       credit_id         AS corresp_id,
       amount            AS debit_amount,
       ( 0.00 ) :: money AS credit_amount
INTO general_ledger
FROM general_journal
UNION
SELECT id                AS gj_id,
       credit_id         AS account_id,
       debit_id          AS corresp_id,
       ( 0.00 ) :: money AS debit_amount,
       amount            AS credit_amount
FROM general_journal
ORDER BY gj_id;
DROP TABLE
SELECT 6
```
Выводим содержимое главной книги:
```sql
SELECT      *
FROM        general_ledger
ORDER BY    gj_id;
 gj_id | account_id | corresp_id | debit_amount | credit_amount 
-------+------------+------------+--------------+---------------
     1 |         10 |         60 |      $400.00 |         $0.00
     1 |         60 |         10 |        $0.00 |       $400.00
     2 |         19 |         60 |       $72.00 |         $0.00
     2 |         60 |         19 |        $0.00 |        $72.00
     3 |         10 |         20 |        $0.00 |        $50.00
     3 |         20 |         10 |       $50.00 |         $0.00
(6 rows)

```
Обороты по счетам:
```sql
SELECT      account_id,
            sum(debit_amount)   AS debit_turnout,
            sum(credit_amount)  AS credit_turnout
FROM        general_ledger
GROUP BY    account_id
ORDER BY    account_id;
 account_id | debit_turnout | credit_turnout 
------------+---------------+----------------
         10 |       $400.00 |         $50.00
         19 |        $72.00 |          $0.00
         20 |        $50.00 |          $0.00
         60 |         $0.00 |        $472.00
(4 rows)

```

Первые две проводки имеют отношение к одному событию - приход материалов. Этому событию могут соответствовать документы: товарно-транспортная накаладная и счет-фактура. Третья проводка - передача материалов со склада в производство. Это событие тоже сопровождается документом, например, накладной.
Таким образом, в general_journal мы можем добавить поле для идентификатора события или операции. А в таблице событий (или операций) организовать связь один-ко-многим с таблицей документов.

Процесс является последовательностью операций. Одним из элементарных операций может быть добавление проводок в бухгалтерскую систему. Для описания процессов может быть добавлена таблица шаблонов процессов.

В России событие прихода материалов в шаблонах будет сопровождаться двумя проводками по счету 10 и 19, а на западе, вероятно, будет одна проводка.

## Step 4. Счет материалы. Аналитический учет

Материалы могут храниться на складах. Добавим склады и используем субсчета.

Файл **step4.sql**:
```sql
DROP TABLE IF EXISTS general_journal;

CREATE TABLE general_journal(
    id              serial,
    debit_id        smallint NOT NULL,
    debit_sub_id    smallint,
    debit_stock_id  smallint,
    credit_id       smallint NOT NULL,
    credit_sub_id   smallint,
    credit_stock_id smallint,
    amount          money NOT NULL
);

DROP TABLE IF EXISTS stock;

CREATE TABLE stock(
    id              serial,
    name            text
);
```
Выполняем проводки с использованием счета 10:
```sql
INSERT INTO general_journal(debit_id, debit_sub_id, debit_stock_id, credit_id, credit_sub_id, credit_stock_id, amount)
VALUES  (10,  1,    1, 60,  1, NULL, 100.00),
        (10,  1,    2, 60,  1, NULL, 200.00),
        (10,  2,    1, 60,  1, NULL, 100.00),
        (19,  3, NULL, 60,  1, NULL,  72.00),
        (20,  3, NULL, 10,  1,    1,  50.00);
INSERT 0 5
```
Выводим содержимое журнала:
```sql
SELECT      *
FROM        general_journal
ORDER BY    id;
 id | debit_id | debit_sub_id | debit_stock_id | credit_id | credit_sub_id | credit_stock_id | amount  
----+----------+--------------+----------------+-----------+---------------+-----------------+---------
  1 |       10 |            1 |              1 |        60 |             1 |                 | $100.00
  2 |       10 |            1 |              2 |        60 |             1 |                 | $200.00
  3 |       10 |            2 |              1 |        60 |             1 |                 | $100.00
  4 |       19 |            3 |                |        60 |             1 |                 |  $72.00
  5 |       20 |            3 |                |        10 |             1 |               1 |  $50.00
(5 rows)

```
Получаем из журнала проводок главную книгу и сохраняем ее в таблице **general_ledger**:
```sql
DROP TABLE IF EXISTS general_ledger;

SELECT id                AS gj_id,
       debit_id          AS acc_id,
       debit_sub_id      AS acc_sub_id,
       debit_stock_id    AS acc_stock_id,
       credit_id         AS cor_id,
       credit_sub_id     AS cor_sub_id,
       credit_stock_id   AS cor_stock_id,
       amount            AS debit_amount,
       ( 0.00 ) :: money AS credit_amount
INTO general_ledger
FROM general_journal
UNION
SELECT id                AS gj_id,
       credit_id         AS acc_id,
       credit_sub_id     AS acc_sub_id,
       credit_stock_id   AS acc_stock_id,
       debit_id          AS cor_id,
       debit_sub_id      AS cor_sub_id,
       debit_stock_id    AS cor_stock_id,
       ( 0.00 ) :: money AS debit_amount,
       amount            AS credit_amount
FROM general_journal
ORDER BY gj_id;
DROP TABLE
SELECT 10
```
Выводим содержимое главной книги:
```sql
SELECT      *
FROM        general_ledger
ORDER BY    gj_id;
 gj_id | acc_id | acc_sub_id | acc_stock_id | cor_id | cor_sub_id | cor_stock_id | debit_amount | credit_amount 
-------+--------+------------+--------------+--------+------------+--------------+--------------+---------------
     1 |     10 |          1 |            1 |     60 |          1 |              |      $100.00 |         $0.00
     1 |     60 |          1 |              |     10 |          1 |            1 |        $0.00 |       $100.00
     2 |     10 |          1 |            2 |     60 |          1 |              |      $200.00 |         $0.00
     2 |     60 |          1 |              |     10 |          1 |            2 |        $0.00 |       $200.00
     3 |     10 |          2 |            1 |     60 |          1 |              |      $100.00 |         $0.00
     3 |     60 |          1 |              |     10 |          2 |            1 |        $0.00 |       $100.00
     4 |     19 |          3 |              |     60 |          1 |              |       $72.00 |         $0.00
     4 |     60 |          1 |              |     19 |          3 |              |        $0.00 |        $72.00
     5 |     10 |          1 |            1 |     20 |          3 |              |        $0.00 |        $50.00
     5 |     20 |          3 |              |     10 |          1 |            1 |       $50.00 |         $0.00
(10 rows)

```
Обороты по счетам:
```sql
SELECT      acc_id,
            sum(debit_amount)   AS debit_turnout,
            sum(credit_amount)  AS credit_turnout
FROM        general_ledger
GROUP BY    acc_id
ORDER BY    acc_id;
 acc_id | debit_turnout | credit_turnout 
--------+---------------+----------------
     10 |       $400.00 |         $50.00
     19 |        $72.00 |          $0.00
     20 |        $50.00 |          $0.00
     60 |         $0.00 |        $472.00
(4 rows)

```
Обороты по субсчетам:
```sql
SELECT      acc_id,
            acc_sub_id,
            sum(debit_amount)   AS debit_turnout,
            sum(credit_amount)  AS credit_turnout
FROM        general_ledger
GROUP BY    acc_id, acc_sub_id
ORDER BY    acc_id, acc_sub_id;
 acc_id | acc_sub_id | debit_turnout | credit_turnout 
--------+------------+---------------+----------------
     10 |          1 |       $300.00 |         $50.00
     10 |          2 |       $100.00 |          $0.00
     19 |          3 |        $72.00 |          $0.00
     20 |          3 |        $50.00 |          $0.00
     60 |          1 |         $0.00 |        $472.00
(5 rows)

```
Обороты по субсчетам и складам:
```sql
SELECT      acc_id,
            acc_sub_id,
            acc_stock_id,
            sum(debit_amount)   AS debit_turnout,
            sum(credit_amount)  AS credit_turnout
FROM        general_ledger
GROUP BY    acc_id, acc_sub_id, acc_stock_id
ORDER BY    acc_id, acc_sub_id, acc_stock_id;
 acc_id | acc_sub_id | acc_stock_id | debit_turnout | credit_turnout 
--------+------------+--------------+---------------+----------------
     10 |          1 |            1 |       $100.00 |         $50.00
     10 |          1 |            2 |       $200.00 |          $0.00
     10 |          2 |            1 |       $100.00 |          $0.00
     19 |          3 |              |        $72.00 |          $0.00
     20 |          3 |              |        $50.00 |          $0.00
     60 |          1 |              |         $0.00 |        $472.00
(6 rows)

```
Обороты только по счету 10 и складам:
```sql
SELECT      acc_stock_id,
            sum(debit_amount)   AS debit_turnout,
            sum(credit_amount)  AS credit_turnout
FROM        general_ledger
WHERE       acc_id = 10
GROUP BY    acc_stock_id
ORDER BY    acc_stock_id;
 acc_stock_id | debit_turnout | credit_turnout 
--------------+---------------+----------------
            1 |       $200.00 |         $50.00
            2 |       $200.00 |          $0.00
(2 rows)

```

Посмотрим на полученный журнал general_journal. Здесь, как видим, для счетов 19, 20 и 60 не нужны идентификаторы складов. Для счета 10 идентификатор склада по дебету нужен только для проводок по этому счету по дебету, и, наоборот, идентификатор склада по кредиту нужен для проводок по этому счету по кредиту. 

Таким образом, мы можем попробовать создать для каждого счета собственный журнал со своим набором полей, то есть с собственной структурой. Попробуем это сделать на следующих днях.

Мы можем добавить поле для количественного учета материалов, которое будет не нужно только для 19 счета. Мы можем добавить для разных счетов другие нужные поля. С добавлением полей будет увеличиваться количество возможных отчетов.

## Step 5. Занимательное

1. Для описания процессов может быть разработана экспертная система. Содержимое главы 10 Knowledge Representation книги [Artificial Intelligence. A Modern Approach](http://aima.cs.berkeley.edu/newchap00.pdf) может быть интересным. Тем более что при разработке плана счетов, при добавлении субсчетов и полей для аналитики затрагиваются темы классификации и онтологии.
Какой-то базовый контент этой экспертной системы будет разработан нами. Например, какой-то базовый контент систем учета для отдельных стран. Остальной контент для разных отраслей и конкретных производств может быть разработан на местах. Разработка и внедрение такого контента вполне может потянуть на суммы озвученные в конкурсной документации РФРИТ [https://ит-гранты.рф/2](https://xn----8sbis2aqlf5f.xn--p1ai/2).
1. Сейчас рассматриваю следующий стэк технологий: PostgreSQL, SQLAlchemy, FastAPI, Svelte/Material.
1. Деплой на десктопы будет выполняться с помощью Ansible.