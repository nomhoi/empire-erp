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
