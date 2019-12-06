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
