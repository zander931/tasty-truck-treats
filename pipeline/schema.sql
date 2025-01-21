-- This file should contain table definitions for the database.

-- DDL
DROP TABLE IF EXISTS FACT_Transaction;
DROP TABLE IF EXISTS DIM_Truck;
DROP TABLE IF EXISTS DIM_Payment_Method;
DROP VIEW IF EXISTS transaction_info;

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
    at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (truck_id) REFERENCES DIM_Truck(truck_id),
    FOREIGN KEY (payment_method_id) REFERENCES DIM_Payment_Method(payment_method_id)
);

SHOW TABLES;

-- DML
INSERT INTO DIM_Truck
    (truck_id, truck_name, truck_description, has_card_reader, fsa_rating)
VALUES
    (1, 'Burrito Madness', 'An authentic taste of Mexico.', TRUE, 4),
    (2, 'Kings of Kebabs', 'Locally-sourced meat cooked over a charcoal grill.', TRUE, 2),
    (3, 'Cupcakes by Michelle', 'Handcrafted cupcakes made with high-quality, organic ingredients.', TRUE, 5),
    (4, 'Hartmann''s Jellied Eels', 'A taste of history with this classic English dish.', TRUE, 4),
    (5, 'Yoghurt Heaven', 'All the great tastes, but only some of the calories!', TRUE, 4),
    (6, 'SuperSmoothie', 'Pick any fruit or vegetable, and we''ll make you a delicious, healthy, multi-vitamin shake. Live well; live wild.', FALSE, 3)
;

INSERT INTO DIM_Payment_Method
    (payment_method_id, payment_method)
VALUES
    (1, 'cash'),
    (2, 'card')
;

-- DQL
CREATE VIEW transaction_info AS (
    SELECT
        transaction_id,
        truck_id,
        t.truck_name,
        total,
        p.payment_method,
        at
    FROM FACT_Transaction
    JOIN DIM_Truck t USING(truck_id)
    JOIN DIM_Payment_Method p USING(payment_method_id)
);