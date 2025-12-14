-- Visitor Management System Database Schema
-- Run this script to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS visitor_management;
USE visitor_management;

-- Admin table for authentication
CREATE TABLE IF NOT EXISTS admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Visitors table to store visitor information
CREATE TABLE IF NOT EXISTS visitors (
    visitor_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    id_proof VARCHAR(50) NOT NULL,
    purpose VARCHAR(200) NOT NULL,
    person_to_meet VARCHAR(100) NOT NULL,
    check_in_time DATETIME,
    check_out_time DATETIME,
    status ENUM('INSIDE', 'EXITED') DEFAULT 'INSIDE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Note: Default admin will be created automatically by Flask app on first run
-- Default credentials: username='admin', password='admin123'
-- The password will be hashed using Werkzeug's generate_password_hash()
-- Run the Flask app once to initialize the default admin user

