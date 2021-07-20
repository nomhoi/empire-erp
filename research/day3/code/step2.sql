DROP TABLE IF EXISTS general_journal;

CREATE TABLE general_journal(
    id              serial,
    debit_id        smallint NOT NULL,
    debit_sub_id    smallint,
    credit_id       smallint NOT NULL,
    credit_sub_id   smallint,
    amount          money NOT NULL
);
