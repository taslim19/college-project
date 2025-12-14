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

-- Appointments table to store appointment requests
-- Created before visitors table to allow foreign key reference
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    visitor_name VARCHAR(100) NOT NULL,
    contact VARCHAR(20) NOT NULL,
    purpose VARCHAR(200) NOT NULL,
    person_to_meet VARCHAR(100) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Visitors table to store visitor information
-- Note: If visitors table already exists, you may need to alter it to add appointment_id column
-- ALTER TABLE visitors ADD COLUMN appointment_id INT NULL;
-- ALTER TABLE visitors ADD FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL;
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
    appointment_id INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE SET NULL
);

-- Note: Default admin will be created automatically by Flask app on first run
-- Default credentials: username='admin', password='admin123'
-- The password will be hashed using Werkzeug's generate_password_hash()
-- Run the Flask app once to initialize the default admin user

-- Future Enhancements (mentioned for viva):
-- - Email notifications for appointment approval/rejection
-- - SMS reminders for upcoming appointments
-- - Calendar integration
-- - Recurring appointments
-- - Appointment cancellation by visitors

