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
