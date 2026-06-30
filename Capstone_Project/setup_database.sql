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
    request_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20),
    issue_description TEXT,
    status VARCHAR(50),
    request_date DATE,
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
