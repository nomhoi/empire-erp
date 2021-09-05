# Empire ERP. Занимательная бухгалтерия: PostgreSQL

Содержание цикла статей: https://github.com/nomhoi/empire-erp.

Попробуем спроектировать базу данных модуля "Бухгалтерия" на PostgreSQL.


## Настройка проекта

Клонируем проект с гитхаба:
```bash
git clone https://github.com/nomhoi/empire-erp.git
```

Заходим в папку **reaserch/day2/**.

## Step 1. Главная книга

Запустим базу данных и выполним тесты:

```bash
docker-compose run test
```

В проекте используется библиотека **pytest-postgresql**. С помощью этой библиотеки создаются фиксации в виде баз данных, которые используются в качестве шаблонов при создании баз данных для каждого теста.

В данном случае создается фиксация на базе **code/step1.sql**:

```sql
DROP TABLE IF EXISTS general_ledger;

CREATE TABLE general_ledger(
    id        serial,
    debit_id  smallint NOT NULL,
    credit_id smallint NOT NULL,
    amount    money NOT NULL
);

INSERT INTO general_ledger(debit_id, credit_id, amount)
VALUES  (1, 12, 100.00),
        (1, 6, 120.00),
        (12, 1, 20.00);

```
Здесь мы создаем таблицу главной книги **general_ledger** и добавляем в нее три проводки.

test_step1.py:

```python
import pytest_postgresql.factories.client
import pytest_postgresql.factories.noprocess
from pytest_postgresql.compat import connection

postgresql_my_proc = pytest_postgresql.factories.noprocess.postgresql_noproc(
    dbname="empire-erp-2", load=["./step1.sql"]
)
postgres = pytest_postgresql.factories.client.postgresql(
    "postgresql_my_proc", dbname="empire-erp-2"
)

def test_1(postgres: connection) -> None:
    with postgres.cursor() as cur:
        cur.execute("SELECT * FROM general_ledger ORDER BY id;")
        res = cur.fetchall()
        assert len(res) == 3
```

Можно выполнить sql запросы вручную. Подключимся к базе данных **empire-erp**:
```bash
docker exec -it db psql -U postgres -d empire-erp
```
Выполняем команду в командной строке **psql** для инициализации базы данных для первого шага:
```
empire-erp=# \i step1.sql
```

Выполняем запрос для получения списка проводок из главной книги:
```sql
SELECT * FROM general_ledger ORDER BY id;
 id | debit_id | credit_id | amount  
----+----------+-----------+---------
  1 |        1 |        12 | $100.00
  2 |        1 |         6 | $120.00
  3 |       12 |         1 |  $20.00
(3 rows)

```

Для получения списка проводок по счету 1 можно выполнить такой запрос:

```sql
SELECT id                AS general_ledger_id,
       credit_id         AS corr_id,
       amount            AS debit_amount,
       ( 0.00 ) :: money AS credit_amount
FROM   general_ledger
WHERE  debit_id = 1
UNION
SELECT id                AS general_ledger_id,
       debit_id          AS corr_id,
       ( 0.00 ) :: money AS debit_amount,
       amount            AS credit_amount
FROM   general_ledger
WHERE  credit_id = 1
ORDER  BY general_ledger_id;
 general_ledger_id | corr_id | debit_amount | credit_amount 
-------------------+---------+--------------+---------------
                 1 |      12 |      $100.00 |         $0.00
                 2 |       6 |      $120.00 |         $0.00
                 3 |      12 |        $0.00 |        $20.00
(3 rows)

```
Или создать функцию **account_entries** :
```sql
DROP FUNCTION IF EXISTS account_entries;

CREATE FUNCTION account_entries(account_id integer)
RETURNS TABLE (
    general_ledger_id   integer,
    corr_id             smallint,
    debit_amount        money,
    credit_amount       money
) AS $$
    SELECT id                AS general_ledger_id,
           credit_id         AS corr_id,
           amount            AS debit_amount,
           ( 0.00 ) :: money AS credit_amount
    FROM   general_ledger
    WHERE  debit_id = account_id
    UNION
    SELECT id                AS general_ledger_id,
           debit_id          AS corr_id,
           ( 0.00 ) :: money AS debit_amount,
           amount            AS credit_amount
    FROM   general_ledger
    WHERE  credit_id = account_id
    ORDER  BY general_ledger_id;
$$ LANGUAGE sql;
```

Выполним команду:
```
empire-erp=# \i step1_3.sql
```

Выполним запрос:
```sql
SELECT * FROM account_entries(1);
 general_ledger_id | corr_id | debit_amount | credit_amount 
-------------------+---------+--------------+---------------
                 1 |      12 |      $100.00 |         $0.00
                 2 |       6 |      $120.00 |         $0.00
                 3 |      12 |        $0.00 |        $20.00
(3 rows)

```

## Step 2. Оборотная ведомость и баланс

Как и в предыдущей статье - все транзакции выполняются в одном отчетном периоде, в начале периода остатки отсутствуют.

Выполним команду:
```
empire-erp=# \i step2.sql
```

Для определения оборотов по счетам выполним такой запрос:
```sql
DROP TABLE IF EXISTS turnout;

SELECT account_id,
       sum(debit_turnout)  AS debit_turnout,
       sum(credit_turnout) AS credit_turnout
INTO   turnout
FROM   (SELECT debit_id          AS account_id,
               sum(amount)       AS debit_turnout,
               ( 0.00 ) :: money AS credit_turnout
        FROM   general_ledger
        GROUP  BY debit_id
        UNION
        SELECT credit_id         AS account_id,
               ( 0.00 ) :: money AS debit_turnout,
               sum(amount)       AS credit_turnout
        FROM   general_ledger
        GROUP  BY credit_id) AS turnout
GROUP  BY account_id
ORDER  BY account_id;

SELECT * FROM turnout;
DROP TABLE
SELECT 3
 account_id | debit_turnout | credit_turnout 
------------+---------------+----------------
          1 |       $220.00 |         $20.00
          6 |         $0.00 |        $120.00
         12 |        $20.00 |        $100.00
(3 rows)

```

Оборотная ведомость
```sql
SELECT start_balance.id            AS account_id,
       start_balance.debit_amount  AS debit_start,
       start_balance.credit_amount AS credit_start,
       turnout.debit_turnout,
       turnout.credit_turnout,
       CASE
         WHEN turnout.debit_turnout + start_balance.debit_amount -
              turnout.credit_turnout - start_balance.credit_amount >= ( 0.0 ) :: money
         THEN turnout.debit_turnout + start_balance.debit_amount -
              turnout.credit_turnout - start_balance.credit_amount
         ELSE ( 0.0 ) :: money
       END                         AS debit_final,
       CASE
         WHEN turnout.credit_turnout + start_balance.credit_amount -
              turnout.debit_turnout - start_balance.debit_amount >= ( 0.0 ) :: money
         THEN turnout.credit_turnout + start_balance.credit_amount -
              turnout.debit_turnout - start_balance.debit_amount
         ELSE ( 0.0 ) :: money
       END                         AS credit_final
FROM   start_balance
       LEFT JOIN turnout
              ON start_balance.id = turnout.account_id;
 account_id | debit_start | credit_start | debit_turnout | credit_turnout | debit_final | credit_final 
------------+-------------+--------------+---------------+----------------+-------------+--------------
          1 |       $0.00 |        $0.00 |       $220.00 |         $20.00 |     $200.00 |        $0.00
          2 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
          3 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
          4 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
          5 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
          6 |       $0.00 |        $0.00 |         $0.00 |        $120.00 |       $0.00 |      $120.00
          7 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
          8 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
          9 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
         10 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
         11 |       $0.00 |        $0.00 |               |                |       $0.00 |        $0.00
         12 |       $0.00 |        $0.00 |        $20.00 |        $100.00 |       $0.00 |       $80.00
(12 rows)

```

Баланс мы получаем из двух последних столбцов оборотной ведомости. Для проверки просуммируем значения столбцов и сверим полученные суммы друг с другом, они должны совпадать. Это уже несложно и я не буду здесь приводить код.

Проблемы со сторно, которая была в прошлой статье сейчас не должно быть, не проверял.

## Step 3. Проверка добавления проводок

На активных счетах остатки могут быть только по дебету, а на пассивных - по кредиту. Будем проверять такие условия.

### 3.1 Проверка уже заполненной главной книги

Допустим, мы занесли все проводки в главную книгу и нужно проверить их на вышеупомянутое условие. Для этого нужно хранить остатки по дебету и кредиту на счетах.

Если пишем на PL/pgSQL, то для хранения остатков по счетам мы можем использовать таблицу с такой структурой:

```sql
CREATE TABLE balance (
    account_id      smallint NOT NULL,
    debit_amount    money DEFAULT 0.0,
    credit_amount   money DEFAULT 0.0
);
```
Если пишем на PL/Python, то можем использовать словарь. Если пишем на C++ - unordered_map.

Алгоритмы проверки остатков на активных и пассивных счетах и обновления остатков на всех счетах в таблице остатков для разных типов счетов различаются. Нужно определять типы счетов каждой проводки. Для определения типа проводки в таблицу плана счетов **coa** (chart of accounts) добавим поле для типа счета: **account_type**:
```sql
CREATE TYPE t_account_type AS ENUM ('active', 'passive', 'active-passive');

CREATE TABLE coa (
    account_id      smallint NOT NULL,
    account_type    t_account_type NOT NULL,
    name            text NOT NULL
);
```
И каким-то образом будем определять с помощью специальной функции. На С++ можно опять использовать unordered_map.

Алгоритмы проверки и определения остатков приводились в прошлой статье, не буду здесь их повторять. Если обнаружится ошибка, то можно поднять исключение и вывести информацию об ошибке.

### 3.2 Проверка на каждом вводе проводки

Можно проверять проводки в момент занесения их в главную книгу. Это можно выполнить с помощью триггерной функции. Триггерная функция будет выполняться после ввода проводки в главную книгу. В случае возникновения ошибки поднимется исключение и транзакция откатится.

На Python и C++ нужно иметь в виду, что в PostgreSQL соединения являются отдельными процессами, поэтому структуру с  остатками нужно хранить в разделяемой между процессами памяти и координировать ее обновление.

### 3.3 Другие ошибки

В этой статье [https://en.wikipedia.org/wiki/Trial_balance](https://en.wikipedia.org/wiki/Trial_balance) указываются несколько ошибок в разделе Limitations. Первая ошибка в нашем случае не проявится, поскольку данные берутся только из главной книги:

> An error of original entry is when both sides of a transaction include the wrong amount.[2] For example, if a purchase invoice for £21 is entered as £12, this will result in an incorrect debit entry (to purchases), and an incorrect credit entry (to the relevant creditor account), both for £9 less, so the total of both columns will be £9 less, and will thus balance.

Остальные ошибки из этой статьи еще не разобрал. Кто разберет и разъяснит всем, тому зарезервирую планету.

## Step 4. Резюме

Как видим, мы можем всю логику модуля "Бухгалтерия" реализовать на стороне сервера базы данных и создать SQL API.
На следующем дне рассмотрим аналитические счета и неможко покодируем на UML.


## Step 5. Занимательное

В этой книге [Artificial Intelligence. A Modern Approach](http://aima.cs.berkeley.edu/newchap00.pdf) есть глава **Automated Planning**. Поскольку ERP про планирование, то имеет смысл добраться до этой главы.

Здесь [https://ит-гранты.рф/2](https://xn----8sbis2aqlf5f.xn--p1ai/2) в конкурсной документации в приложении #3 видим, что ERP системы имеют приоритет 1-го порядка, надо посмотреть требования.



