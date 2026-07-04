-- Database Initialization Script
-- Run this in your MySQL environment to set up the structure

CREATE DATABASE IF NOT EXISTS smart_warranty_db;
USE smart_warranty_db;

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    purchase_date DATE,
    price DECIMAL(10, 2)
);

-- Warranties Table
CREATE TABLE IF NOT EXISTS warranties (
    warranty_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20),
    warranty_start_date DATE,
    warranty_end_date DATE,
    terms_summary TEXT,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Service Requests Table
CREATE TABLE IF NOT EXISTS service_requests (
    request_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(255),
    issue_description TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Documents Table
CREATE TABLE IF NOT EXISTS documents (
    doc_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20),
    doc_type VARCHAR(50),
    file_path VARCHAR(255),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);


show DATABASES;
use smart_warranty_db;
show tables;
DESCRIBE warranties;
select * from warranties;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM warranties;
SELECT COUNT(*) FROM service_requests;
SELECT COUNT(*) FROM documents;