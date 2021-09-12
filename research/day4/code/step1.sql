DROP TABLE IF EXISTS operation;

CREATE TABLE operation(
    id          serial,
    name        text         
);


DROP TABLE IF EXISTS journal_10;

CREATE TABLE journal_10(
    id          serial,
    op_id       smallint NOT NULL,
    side        smallint NOT NULL,
    acc_id      smallint NOT NULL,
    acc_sub_id  smallint,    
    amount      money NOT NULL,
    stock_id    smallint
);


DROP TABLE IF EXISTS journal_19;

CREATE TABLE journal_19(
    id          serial,
    op_id       smallint NOT NULL,
    side        smallint NOT NULL,
    acc_id      smallint NOT NULL,
    acc_sub_id  smallint,    
    amount      money NOT NULL
);


DROP TABLE IF EXISTS journal_20;

CREATE TABLE journal_20(
    id          serial,
    op_id       smallint NOT NULL,
    side        smallint NOT NULL,
    acc_id      smallint NOT NULL,
    acc_sub_id  smallint,
    amount      money NOT NULL    
);


DROP TABLE IF EXISTS journal_60;

CREATE TABLE journal_60(
    id          serial,
    op_id       smallint NOT NULL,
    side        smallint NOT NULL,
    acc_id      smallint NOT NULL,
    acc_sub_id  smallint,
    amount      money NOT NULL,
    supplier_id smallint NOT NULL    
);


DROP TABLE IF EXISTS stock;

CREATE TABLE stock(
    id              serial,
    name            text
);
