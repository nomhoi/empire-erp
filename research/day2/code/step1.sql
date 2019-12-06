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

