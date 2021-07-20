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