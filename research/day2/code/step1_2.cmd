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
