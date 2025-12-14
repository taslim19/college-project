# Appointment Module Setup Guide

## Overview
The Appointment Visitor Module has been added to extend the existing Visitor Management System. This module allows visitors to book appointments in advance, which can then be approved by admins and converted into visitor entries.

## Database Setup

### For New Installations
Simply run the updated `schema.sql` file. It will create:
- `appointments` table
- Updated `visitors` table with `appointment_id` column

### For Existing Installations
If you already have the `visitors` table, you need to add the appointments table and update the visitors table:

```sql
-- 1. Create appointments table
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

-- 2. Add appointment_id column to existing visitors table
ALTER TABLE visitors ADD COLUMN appointment_id INT NULL;

-- 3. Add foreign key constraint
ALTER TABLE visitors 
ADD CONSTRAINT fk_appointment 
FOREIGN KEY (appointment_id) 
REFERENCES appointments(appointment_id) 
ON DELETE SET NULL;
```

## Features

### Visitor Features
- **Book Appointment** (`/book-appointment`): Public page where visitors can submit appointment requests
- No authentication required for booking
- Date validation (must be today or future)

### Admin Features
- **View Appointments** (`/appointments`): View all appointment requests with status filters
- **Approve Appointment**: Change status from PENDING to APPROVED
- **Reject Appointment**: Change status from PENDING to REJECTED
- **Convert Appointment**: Convert approved appointments into visitor entries
  - Only works for approved appointments
  - Only works if appointment date is today or in the past
  - Prevents duplicate conversions
  - Automatically sets visitor status to INSIDE
  - Links visitor record to appointment via `appointment_id`

## Workflow

1. **Visitor books appointment** → Status: PENDING
2. **Admin reviews and approves** → Status: APPROVED
3. **On appointment date, admin converts** → Creates visitor entry with status INSIDE
4. **Visitor checks out normally** → Status: EXITED

## Routes Added

- `GET/POST /book-appointment` - Public appointment booking page
- `GET /appointments` - Admin appointment management (requires login)
- `GET /approve-appointment/<id>` - Approve an appointment (requires login)
- `GET /reject-appointment/<id>` - Reject an appointment (requires login)
- `GET /convert-appointment/<id>` - Convert appointment to visitor (requires login)

## Database Schema

### Appointments Table
- `appointment_id` (Primary Key)
- `visitor_name`
- `contact`
- `purpose`
- `person_to_meet`
- `appointment_date`
- `appointment_time`
- `status` (PENDING, APPROVED, REJECTED)
- `created_at`

### Updated Visitors Table
- Added: `appointment_id` (Foreign Key, nullable)

## Security Notes

- All admin routes require `@login_required` decorator
- Appointment booking is public (no authentication)
- Conversion logic validates appointment status and date
- Prevents duplicate conversions

## Future Enhancements (mentioned in code comments)

- Email notifications for appointment approval/rejection
- SMS reminders for upcoming appointments
- Calendar integration
- Recurring appointments
- Appointment cancellation by visitors
- ID proof collection during appointment booking

## Testing

1. Book an appointment as a visitor
2. Login as admin and view appointments
3. Approve the appointment
4. Convert the appointment to a visitor entry
5. Verify the visitor appears in the dashboard

## Notes

- Existing visitor management functionality remains unchanged
- Appointment module is cleanly separated from visitor logic
- All appointment-related code is well-commented
- Follows the same coding style as the existing project

