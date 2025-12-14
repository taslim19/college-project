# Visitor Management System

A secure, automated digital system to replace traditional manual visitor registers. Built with Python Flask and MySQL.

## Features

- **Visitor Registration**: Capture visitor details (name, contact, ID proof, purpose, person to meet) and generate unique visitor IDs
- **Check-In System**: Automatically record visitor check-in time and set status to INSIDE
- **Check-Out System**: Automatically record visitor check-out time and update status to EXITED
- **Admin Authentication**: Secure login using username and password with session-based authentication
- **Admin Dashboard**: View visitors currently inside, total visitors for the day, and recent visitor history
- **Reports Module**: Generate daily and monthly visitor reports in tabular format

## Technology Stack

- **Backend**: Python Flask
- **Database**: MySQL
- **Frontend**: HTML, CSS, Bootstrap 5, JavaScript
- **Templates**: Jinja2

## Prerequisites

- Python 3.7 or higher
- MySQL Server 5.7 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Clone or Download the Project

```bash
# Navigate to project directory
cd visitor-management-system
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup MySQL Database

1. Start MySQL server
2. Open MySQL command line or MySQL Workbench
3. Run the schema file to create database and tables:

```bash
mysql -u root -p < schema.sql
```

Or manually execute the SQL commands from `schema.sql` in MySQL.

### 4. Configure Database Connection

Edit `app.py` and update the database configuration:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',  # Update this
    'database': 'visitor_management'
}
```

### 5. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`

**Note**: Change the default password after first login in production.

## Project Structure

```
visitor-management-system/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── schema.sql            # Database schema
├── README.md             # This file
│
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── login.html       # Admin login page
│   ├── register.html    # Visitor registration
│   ├── checkin.html     # Check-in page
│   ├── checkout.html    # Check-out page
│   ├── dashboard.html   # Admin dashboard
│   ├── reports.html     # Reports page
│   └── error.html       # Error page
│
└── static/              # Static files (CSS, JS, images)
```

## Usage Guide

### For Visitors

1. **Registration**: Visit the registration page and fill in all required details
2. **Note your Visitor ID**: After registration, you'll receive a unique visitor ID
3. **Check-In**: Provide your visitor ID at the check-in counter
4. **Check-Out**: Provide your visitor ID when leaving

### For Administrators

1. **Login**: Use admin credentials to access the system
2. **Dashboard**: View current visitors and statistics
3. **Register Visitors**: Add new visitors to the system
4. **Check-In/Check-Out**: Process visitor check-ins and check-outs
5. **Reports**: Generate daily or monthly visitor reports

## Database Schema

### Admin Table
- `admin_id` (Primary Key)
- `username` (Unique)
- `password` (Hashed)
- `created_at`

### Visitors Table
- `visitor_id` (Primary Key, Auto-generated)
- `name`
- `contact`
- `id_proof`
- `purpose`
- `person_to_meet`
- `check_in_time`
- `check_out_time`
- `status` (INSIDE/EXITED)
- `created_at`

## Security Features

- Password hashing using Werkzeug's security utilities
- Session-based authentication
- Input validation on all forms
- SQL injection prevention using parameterized queries
- Protected routes with login decorator

## Future Enhancements

The following features are planned for future implementation (mentioned in code comments):

- **QR Code Passes**: Generate QR codes for visitors
- **SMS Notifications**: Send SMS alerts for check-in/check-out
- **Biometric Verification**: Fingerprint or face recognition
- **Email Notifications**: Email alerts to hosts
- **Visitor Photo Capture**: Store visitor photographs
- **Advanced Analytics**: Charts and graphs for visitor trends
- **Multi-building Support**: Manage multiple buildings/locations

## Troubleshooting

### Database Connection Error

- Ensure MySQL server is running
- Verify database credentials in `app.py`
- Check if database `visitor_management` exists

### Module Not Found Error

- Install all dependencies: `pip install -r requirements.txt`
- Ensure you're using Python 3.7+

### Port Already in Use

- Change the port in `app.py`: `app.run(port=5001)`
- Or stop the process using port 5000

## Viva/Exam Notes

### Key Points to Explain

1. **Flask Framework**: Lightweight web framework, routing, templates
2. **MySQL Integration**: Database connection, CRUD operations
3. **Session Management**: User authentication, protected routes
4. **Security**: Password hashing, input validation, SQL injection prevention
5. **Jinja2 Templates**: Template inheritance, dynamic content
6. **RESTful Routes**: GET/POST methods, URL routing

### Common Questions

- **Why Flask?** Lightweight, flexible, easy to learn, perfect for small to medium applications
- **Why MySQL?** Reliable, widely used, good for structured data
- **Security Measures?** Password hashing, session management, input validation, parameterized queries
- **Database Design?** Normalized tables, proper relationships, indexes for performance

## License

This project is created for educational purposes.

## Author

Created for college project/viva examination.

