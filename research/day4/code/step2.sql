DROP TABLE IF EXISTS operation;

CREATE TABLE operation(
    id          serial,
    name        text         
);


DROP TABLE IF EXISTS ledger_10;

CREATE TABLE ledger_10(
    id              serial,
    op_id           smallint NOT NULL,
    acc_id          smallint NOT NULL,
    acc_sub_id      smallint NOT NULL,    
    debit_amount    money NOT NULL,
    credit_amount   money NOT NULL,
    stock_id        smallint
);


DROP TABLE IF EXISTS ledger_19;

CREATE TABLE ledger_19(
    id              serial,
    op_id           smallint NOT NULL,
    acc_id          smallint NOT NULL,
    acc_sub_id      smallint NOT NULL,    
    debit_amount    money NOT NULL,
    credit_amount   money NOT NULL
);


DROP TABLE IF EXISTS ledger_20;

CREATE TABLE ledger_20(
    id              serial,
    op_id           smallint NOT NULL,
    acc_id          smallint NOT NULL,
    acc_sub_id      smallint NOT NULL,
    debit_amount    money NOT NULL,
    credit_amount   money NOT NULL
);


DROP TABLE IF EXISTS ledger_60;

CREATE TABLE ledger_60(
    id              serial,
    op_id           smallint NOT NULL,
    acc_id          smallint NOT NULL,
    acc_sub_id      smallint NOT NULL,
    debit_amount    money NOT NULL,
    credit_amount   money NOT NULL,
    supplier_id     smallint NOT NULL    
);


DROP TABLE IF EXISTS stock;

CREATE TABLE stock(
    id              serial,
    name            text
);
