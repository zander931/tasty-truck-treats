-- This file should contain table definitions for the database.

DROP TABLE IF EXISTS FACT_Transaction;
DROP TABLE IF EXISTS DIM_Truck;
DROP TABLE IF EXISTS DIM_Payment_Method;

CREATE TABLE IF NOT EXISTS DIM_Payment_Method (
    payment_method_id SMALLINT PRIMARY KEY,
    payment_method VARCHAR(10) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS DIM_Truck (
    truck_id SMALLINT PRIMARY KEY,
    truck_name VARCHAR(255) UNIQUE NOT NULL,
    truck_description TEXT,
    has_card_reader BOOLEAN NOT NULL,
    fsa_rating SMALLINT CHECK (fsa_rating BETWEEN 1 AND 5)
);

CREATE TABLE IF NOT EXISTS FACT_Transaction (
    transaction_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    truck_id SMALLINT NOT NULL,
    payment_method_id SMALLINT NOT NULL,
    total DECIMAL(3,2) NOT NULL,
    at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (truck_id) REFERENCES DIM_Truck(truck_id),
    FOREIGN KEY (payment_method_id) REFERENCES DIM_Payment_Method(payment_method_id)
);
