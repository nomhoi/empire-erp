# Empire ERP. Занимательная бухгалтерия: Аналитический учет, ч.2.

Содержание цикла статей: https://github.com/nomhoi/empire-erp.

Продолжаем рассмотрение аналитического учета.

## Настройка проекта

Клонируем проект с гитхаба:
```bash
git clone https://github.com/nomhoi/empire-erp.git
```

Заходим в папку **reaserch/day4/**.

Запустим базу данных и выполним тесты:

```bash
docker-compose run test
```

Подключимся к базе данных **empire-erp**:
```bash
docker exec -it db psql -U postgres -d empire-erp
```

## Step 1. Вспомогательные журналы

Выполним команду в командной строке **psql** для инициализации базы данных:
```
empire-erp=# \i step1.sql
```

Создадим вспомогательные журналы проводок аналитического учета.

Файл **step1.sql**:
```sql
DROP TABLE IF EXISTS operation;

CREATE TABLE operation(
    id          serial,
    name        text         
);


DROP TABLE IF EXISTS journal_10;

CREATE TABLE journal_10(
    id          serial,
    op_id       smallint NOT NULL,
    side        smallint NOT NULL,
    acc_id      smallint NOT NULL,
    acc_sub_id  smallint,    
    amount      money NOT NULL,
    stock_id    smallint
);


DROP TABLE IF EXISTS journal_19;

CREATE TABLE journal_19(
    id          serial,
    op_id       smallint NOT NULL,
    side        smallint NOT NULL,
    acc_id      smallint NOT NULL,
    acc_sub_id  smallint,    
    amount      money NOT NULL
);


DROP TABLE IF EXISTS journal_20;

CREATE TABLE journal_20(
    id          serial,
    op_id       smallint NOT NULL,
    side        smallint NOT NULL,
    acc_id      smallint NOT NULL,
    acc_sub_id  smallint,
    amount      money NOT NULL    
);


DROP TABLE IF EXISTS journal_60;

CREATE TABLE journal_60(
    id          serial,
    op_id       smallint NOT NULL,
    side        smallint NOT NULL,
    acc_id      smallint NOT NULL,
    acc_sub_id  smallint,
    amount      money NOT NULL,
    supplier_id smallint NOT NULL    
);


DROP TABLE IF EXISTS stock;

CREATE TABLE stock(
    id              serial,
    name            text
);
```

Заполним вспомогательные журналы проводок исходными данными:
```sql
-- 1. Поступление материалов

INSERT INTO operation(id , name)
VALUES  (1, 'Поступление материалов');

INSERT INTO journal_10(op_id, side, acc_id, acc_sub_id, stock_id, amount)
VALUES  (1, 0, 10, 1, 1, 100.00),
        (1, 0, 10, 1, 2, 200.00),
        (1, 0, 10, 2, 1, 100.00);

INSERT INTO journal_60(op_id, side, acc_id, acc_sub_id, supplier_id, amount)
VALUES  (1, 1, 60, 1, 3, 100.00),
        (1, 1, 60, 1, 3, 200.00),
        (1, 1, 60, 1, 3, 100.00);

-- 2. Начисление НДС

INSERT INTO operation(id , name)
VALUES  (2, 'Начисление НДС');

INSERT INTO journal_60(op_id, side, acc_id, acc_sub_id, supplier_id, amount)
VALUES  (2, 1, 60, 1, 3,  72.00);

INSERT INTO journal_19(op_id, side, acc_id, acc_sub_id, amount)
VALUES  (2, 0, 19, 3, 72.00);

-- 3. Перевод материалов в производство

INSERT INTO operation(id , name)
VALUES  (3, 'Перевод материалов в производство');

INSERT INTO journal_10(op_id, side, acc_id, acc_sub_id, stock_id, amount)
VALUES  (3, 1, 10, 1, 1,  50.00);

INSERT INTO journal_20(op_id, side, acc_id, acc_sub_id, amount)
VALUES  (3, 0, 20, 3, 50.00);

INSERT 0 1
INSERT 0 3
INSERT 0 3
INSERT 0 1
INSERT 0 1
INSERT 0 1
INSERT 0 1
INSERT 0 1
INSERT 0 1
```

Выводим содержимое вспомогательных журналов:
```sql
SELECT      *
FROM        journal_10
ORDER BY    id;

SELECT      *
FROM        journal_19
ORDER BY    id;

SELECT      *
FROM        journal_20
ORDER BY    id;

SELECT      *
FROM        journal_60
ORDER BY    id;

 id | op_id | side | acc_id | acc_sub_id | amount  | stock_id 
----+-------+------+--------+------------+---------+----------
  1 |     1 |    0 |     10 |          1 | $100.00 |        1
  2 |     1 |    0 |     10 |          1 | $200.00 |        2
  3 |     1 |    0 |     10 |          2 | $100.00 |        1
  4 |     3 |    1 |     10 |          1 |  $50.00 |        1
(4 rows)

 id | op_id | side | acc_id | acc_sub_id | amount 
----+-------+------+--------+------------+--------
  1 |     2 |    0 |     19 |          3 | $72.00
(1 row)

 id | op_id | side | acc_id | acc_sub_id | amount 
----+-------+------+--------+------------+--------
  1 |     3 |    0 |     20 |          3 | $50.00
(1 row)

 id | op_id | side | acc_id | acc_sub_id | amount  | supplier_id 
----+-------+------+--------+------------+---------+-------------
  1 |     1 |    1 |     60 |          1 | $100.00 |           3
  2 |     1 |    1 |     60 |          1 | $200.00 |           3
  3 |     1 |    1 |     60 |          1 | $100.00 |           3
  4 |     2 |    1 |     60 |          1 |  $72.00 |           3
(4 rows)

```

Обороты по счету 10:
```sql
SELECT      acc_id,
            sum(
                CASE 
                    WHEN side = 0
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS debit_turnout,
            sum(
                CASE 
                    WHEN side = 1
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS credit_turnout
FROM        journal_10
GROUP BY    acc_id;

 acc_id | debit_turnout | credit_turnout 
--------+---------------+----------------
     10 |       $400.00 |         $50.00
(1 row)

```

Обороты по счету 10 и субсчетам:
```sql
SELECT      acc_id,
            acc_sub_id,
            sum(
                CASE 
                    WHEN side = 0
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS debit_turnout,
            sum(
                CASE 
                    WHEN side = 1
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS credit_turnout
FROM        journal_10
GROUP BY    acc_id, acc_sub_id
ORDER BY    acc_id, acc_sub_id;

 acc_id | acc_sub_id | debit_turnout | credit_turnout 
--------+------------+---------------+----------------
     10 |          1 |       $300.00 |         $50.00
     10 |          2 |       $100.00 |          $0.00
(2 rows)

```

Обороты по счету 10, субсчетам и складам:
```sql
SELECT      acc_id,
            acc_sub_id,
            stock_id,
            sum(
                CASE 
                    WHEN side = 0
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS debit_turnout,
            sum(
                CASE 
                    WHEN side = 1
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS credit_turnout
FROM        journal_10
GROUP BY    acc_id, acc_sub_id, stock_id
ORDER BY    acc_id, acc_sub_id, stock_id;

 acc_id | acc_sub_id | stock_id | debit_turnout | credit_turnout 
--------+------------+----------+---------------+----------------
     10 |          1 |        1 |       $100.00 |         $50.00
     10 |          1 |        2 |       $200.00 |          $0.00
     10 |          2 |        1 |       $100.00 |          $0.00
(3 rows)

```

Проверим проведение сторно и получим обороты по счету 10, субсчетам и складам:
```sql
INSERT INTO journal_10(op_id, side, acc_id, acc_sub_id, stock_id, amount)
VALUES  (4, 0, 10, 1, 1, 100.00),
        (5, 0, 10, 1, 1,-100.00);

INSERT INTO journal_60(op_id, side, acc_id, acc_sub_id, supplier_id, amount)
VALUES  (4, 1, 60, 1, 3, 100.00),
        (5, 1, 60, 1, 3,-100.00);

SELECT      acc_id,
            acc_sub_id,
            stock_id,
            sum(
                CASE 
                    WHEN side = 0
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS debit_turnout,
            sum(
                CASE 
                    WHEN side = 1
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS credit_turnout
FROM        journal_10
GROUP BY    acc_id, acc_sub_id, stock_id
ORDER BY    acc_id, acc_sub_id, stock_id;

INSERT 0 2
INSERT 0 2
 acc_id | acc_sub_id | stock_id | debit_turnout | credit_turnout 
--------+------------+----------+---------------+----------------
     10 |          1 |        1 |       $100.00 |         $50.00
     10 |          1 |        2 |       $200.00 |          $0.00
     10 |          2 |        1 |       $100.00 |          $0.00
(3 rows)

```

Обороты по счетам:
```sql
DROP TABLE IF EXISTS turnout;

CREATE TABLE turnout(
    acc_id          smallint NOT NULL,
    debit_turnout   money NOT NULL,
    credit_turnout  money NOT NULL
);

INSERT INTO turnout
SELECT      acc_id,
            sum(
                CASE 
                    WHEN side = 0
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS debit_turnout,
            sum(
                CASE 
                    WHEN side = 1
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS credit_turnout
FROM        journal_10
GROUP BY    acc_id;

INSERT INTO turnout
SELECT      acc_id,
            sum(
                CASE 
                    WHEN side = 0
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS debit_turnout,
            sum(
                CASE 
                    WHEN side = 1
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS credit_turnout
FROM        journal_19
GROUP BY    acc_id;

INSERT INTO turnout
SELECT      acc_id,
            sum(
                CASE 
                    WHEN side = 0
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS debit_turnout,
            sum(
                CASE 
                    WHEN side = 1
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS credit_turnout
FROM        journal_20
GROUP BY    acc_id;

INSERT INTO turnout
SELECT      acc_id,
            sum(
                CASE 
                    WHEN side = 0
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS debit_turnout,
            sum(
                CASE 
                    WHEN side = 1
                    THEN amount
                    ELSE (0.0)::money
                END
            ) AS credit_turnout
FROM        journal_60
GROUP BY    acc_id;

SELECT      *
FROM        turnout
ORDER BY    acc_id;

DROP TABLE
CREATE TABLE
INSERT 0 1
INSERT 0 1
INSERT 0 1
INSERT 0 1
 acc_id | debit_turnout | credit_turnout 
--------+---------------+----------------
     10 |       $400.00 |         $50.00
     19 |        $72.00 |          $0.00
     20 |        $50.00 |          $0.00
     60 |         $0.00 |        $472.00
(4 rows)

```
