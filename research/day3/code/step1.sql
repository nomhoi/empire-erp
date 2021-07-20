DROP TABLE IF EXISTS general_journal;

CREATE TABLE general_journal(
    id        serial,
    debit_id  smallint NOT NULL,
    credit_id smallint NOT NULL,
    amount    money NOT NULL
);
