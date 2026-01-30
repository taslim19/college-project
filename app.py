"""
Visitor Management System
A secure, automated digital system to replace traditional manual visitor registers.

Future Enhancements (mentioned for viva):
- QR code passes for visitors
- SMS notifications for check-in/check-out
- Biometric verification
- Email notifications
- Visitor photo capture
- Appointment module with email/SMS notifications
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update with your MySQL password
    'database': 'visitor_management'
}


def get_db_connection():
    """
    Create and return a database connection.
    Handles connection errors gracefully.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def init_database():
    """
    Initialize database with tables and default admin if not exists.
    Creates appointments table and admin user automatically.
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            
            # Create appointments table if it doesn't exist
            try:
                cursor.execute("""
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
                    )
                """)
                conn.commit()
                print("Appointments table checked/created successfully")
            except Error as e:
                print(f"Note: Appointments table may already exist: {e}")
            
            # Add appointment_id column to visitors table if it doesn't exist
            try:
                cursor.execute("""
                    SELECT COLUMN_NAME 
                    FROM INFORMATION_SCHEMA.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() 
                    AND TABLE_NAME = 'visitors' 
                    AND COLUMN_NAME = 'appointment_id'
                """)
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE visitors ADD COLUMN appointment_id INT NULL")
                    # Add foreign key constraint if appointments table exists
                    try:
                        cursor.execute("""
                            ALTER TABLE visitors 
                            ADD CONSTRAINT fk_appointment 
                            FOREIGN KEY (appointment_id) 
                            REFERENCES appointments(appointment_id) 
                            ON DELETE SET NULL
                        """)
                    except Error:
                        # Foreign key might already exist or appointments table doesn't exist yet
                        pass
                    conn.commit()
                    print("Added appointment_id column to visitors table")
            except Error as e:
                print(f"Note: appointment_id column may already exist: {e}")
            
            # Check if admin exists
            try:
                cursor.execute("SELECT COUNT(*) FROM admin WHERE username = 'admin'")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # Create default admin
                    hashed_password = generate_password_hash('admin123')
                    cursor.execute(
                        "INSERT INTO admin (username, password) VALUES (%s, %s)",
                        ('admin', hashed_password)
                    )
                    conn.commit()
                    print("Default admin created: username='admin', password='admin123'")
            except Error as e:
                print(f"Note: Admin table may not exist yet. Run schema.sql first: {e}")
            
            cursor.close()
            conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")
        print("Please ensure the database and base tables (admin, visitors) exist. Run schema.sql if needed.")


# Initialize database on startup
init_database()


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def home():
    # This renders the new Landing Page (index.html) we created
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Admin login page.
    Uses session-based authentication.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Input validation
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM admin WHERE username = %s",
                (username,)
            )
            admin = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if admin and check_password_hash(admin['password'], password):
                # Set session
                session['admin_id'] = admin['admin_id']
                session['username'] = admin['username']
                session['logged_in'] = True
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))


def login_required(f):
    """
    Decorator to protect routes that require authentication.
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Please login to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== VISITOR REGISTRATION ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Visitor registration page.
    Captures: name, contact, ID proof, purpose, person to meet.
    Generates unique visitor ID.
    """
    if request.method == 'POST':
        name = request.form.get('name')
        contact = request.form.get('contact')
        id_proof = request.form.get('id_proof')
        purpose = request.form.get('purpose')
        person_to_meet = request.form.get('person_to_meet')
        
        # Input validation
        if not all([name, contact, id_proof, purpose, person_to_meet]):
            flash('Please fill all fields', 'error')
            return render_template('register.html')
        
        # Validate contact number (basic validation)
        if not contact.isdigit() or len(contact) < 10:
            flash('Please enter a valid contact number', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Insert visitor (visitor_id is auto-generated)
                cursor.execute(
                    """INSERT INTO visitors (name, contact, id_proof, purpose, person_to_meet, 
                       check_in_time, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (name, contact, id_proof, purpose, person_to_meet, datetime.now(), 'INSIDE')
                )
                conn.commit()
                visitor_id = cursor.lastrowid
                cursor.close()
                conn.close()
                
                flash(f'Visitor registered successfully! Visitor ID: {visitor_id}', 'success')
                return redirect(url_for('register'))
            except Error as e:
                flash(f'Error registering visitor: {str(e)}', 'error')
        
    return render_template('register.html')


# ==================== CHECK-IN SYSTEM ====================

@app.route('/checkin', methods=['GET', 'POST'])
@login_required
def checkin():
    """
    Visitor check-in page.
    Records check-in time and sets status to INSIDE.
    """
    if request.method == 'POST':
        visitor_id = request.form.get('visitor_id')
        
        if not visitor_id:
            flash('Please enter visitor ID', 'error')
            return render_template('checkin.html')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Check if visitor exists
            cursor.execute(
                "SELECT * FROM visitors WHERE visitor_id = %s",
                (visitor_id,)
            )
            visitor = cursor.fetchone()
            
            if visitor:
                # Check if already checked in
                if visitor['status'] == 'INSIDE' and visitor['check_in_time']:
                    flash('Visitor is already checked in', 'warning')
                else:
                    # Update check-in
                    cursor.execute(
                        """UPDATE visitors SET check_in_time = %s, status = 'INSIDE' 
                           WHERE visitor_id = %s""",
                        (datetime.now(), visitor_id)
                    )
                    conn.commit()
                    flash(f'Visitor {visitor["name"]} checked in successfully!', 'success')
            else:
                flash('Visitor ID not found', 'error')
            
            cursor.close()
            conn.close()
        
    return render_template('checkin.html')


# ==================== CHECK-OUT SYSTEM ====================

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    Visitor check-out page.
    Records check-out time and sets status to EXITED.
    """
    if request.method == 'POST':
        visitor_id = request.form.get('visitor_id')
        
        if not visitor_id:
            flash('Please enter visitor ID', 'error')
            return render_template('checkout.html')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            # Check if visitor exists
            cursor.execute(
                "SELECT * FROM visitors WHERE visitor_id = %s",
                (visitor_id,)
            )
            visitor = cursor.fetchone()
            
            if visitor:
                # Check if already checked out
                if visitor['status'] == 'EXITED':
                    flash('Visitor has already checked out', 'warning')
                elif visitor['status'] == 'INSIDE':
                    # Update check-out
                    cursor.execute(
                        """UPDATE visitors SET check_out_time = %s, status = 'EXITED' 
                           WHERE visitor_id = %s""",
                        (datetime.now(), visitor_id)
                    )
                    conn.commit()
                    flash(f'Visitor {visitor["name"]} checked out successfully!', 'success')
                else:
                    flash('Visitor needs to check in first', 'error')
            else:
                flash('Visitor ID not found', 'error')
            
            cursor.close()
            conn.close()
        
    return render_template('checkout.html')


# ==================== ADMIN DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """
    Admin dashboard.
    Displays:
    - Visitors currently inside
    - Total visitors for today
    - Recent visitor history
    """
    conn = get_db_connection()
    visitors_inside = []
    total_today = 0
    recent_visitors = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Get visitors currently inside
        cursor.execute(
            """SELECT * FROM visitors WHERE status = 'INSIDE' 
               ORDER BY check_in_time DESC"""
        )
        visitors_inside = cursor.fetchall()
        
        # Get total visitors for today
        today = date.today()
        cursor.execute(
            """SELECT COUNT(*) as count FROM visitors 
               WHERE DATE(check_in_time) = %s""",
            (today,)
        )
        total_today = cursor.fetchone()['count']
        
        # Get recent visitors (last 10)
        cursor.execute(
            """SELECT * FROM visitors 
               ORDER BY created_at DESC LIMIT 10"""
        )
        recent_visitors = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return render_template('dashboard.html', 
                         visitors_inside=visitors_inside,
                         total_today=total_today,
                         recent_visitors=recent_visitors)


# ==================== REPORTS MODULE ====================

@app.route('/reports', methods=['GET', 'POST'])
@login_required
def reports():
    """
    Reports page.
    Generates daily and monthly visitor reports.
    """
    report_type = request.args.get('type', 'daily')
    selected_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    selected_month = request.args.get('month', date.today().strftime('%Y-%m'))
    
    visitors = []
    conn = get_db_connection()
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        if report_type == 'daily':
            # Daily report
            cursor.execute(
                """SELECT * FROM visitors 
                   WHERE DATE(check_in_time) = %s 
                   ORDER BY check_in_time DESC""",
                (selected_date,)
            )
            visitors = cursor.fetchall()
        elif report_type == 'monthly':
            # Monthly report
            year, month = selected_month.split('-')
            cursor.execute(
                """SELECT * FROM visitors 
                   WHERE YEAR(check_in_time) = %s AND MONTH(check_in_time) = %s 
                   ORDER BY check_in_time DESC""",
                (year, month)
            )
            visitors = cursor.fetchall()
        
        cursor.close()
        conn.close()
    
    return render_template('reports.html',
                         visitors=visitors,
                         report_type=report_type,
                         selected_date=selected_date,
                         selected_month=selected_month)


# ==================== APPOINTMENT MODULE ====================

@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    """
    Visitor-facing appointment booking page.
    Allows visitors to submit appointment requests.
    No authentication required.
    """
    if request.method == 'POST':
        visitor_name = request.form.get('visitor_name')
        contact = request.form.get('contact')
        purpose = request.form.get('purpose')
        person_to_meet = request.form.get('person_to_meet')
        appointment_date = request.form.get('appointment_date')
        appointment_time = request.form.get('appointment_time')
        
        # Pass today's date for template
        today = date.today().strftime('%Y-%m-%d')
        
        # Input validation
        if not all([visitor_name, contact, purpose, person_to_meet, appointment_date, appointment_time]):
            flash('Please fill all fields', 'error')
            return render_template('book_appointment.html', today=today)
        
        # Validate contact number
        if not contact.isdigit() or len(contact) < 10:
            flash('Please enter a valid contact number', 'error')
            return render_template('book_appointment.html', today=today)
        
        # Validate appointment date (should be in the future)
        try:
            appt_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            if appt_date < date.today():
                flash('Appointment date must be today or in the future', 'error')
                return render_template('book_appointment.html', today=today)
        except ValueError:
            flash('Invalid date format', 'error')
            return render_template('book_appointment.html', today=today)
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # Insert appointment request with PENDING status
                cursor.execute(
                    """INSERT INTO appointments (visitor_name, contact, purpose, person_to_meet, 
                       appointment_date, appointment_time, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, 'PENDING')""",
                    (visitor_name, contact, purpose, person_to_meet, appointment_date, appointment_time)
                )
                conn.commit()
                appointment_id = cursor.lastrowid
                cursor.close()
                conn.close()
                
                flash(f'Appointment request submitted successfully! Your Appointment ID: {appointment_id}. Please wait for admin approval.', 'success')
                return redirect(url_for('book_appointment'))
            except Error as e:
                flash(f'Error submitting appointment: {str(e)}', 'error')
        
    # Pass date to template for min date validation
    today = date.today().strftime('%Y-%m-%d')
    return render_template('book_appointment.html', today=today)


@app.route('/appointments')
@login_required
def appointments():
    """
    Admin page to view all appointment requests.
    Shows appointments with filters for status.
    """
    status_filter = request.args.get('status', 'all')
    
    conn = get_db_connection()
    appointments_list = []
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        if status_filter == 'all':
            cursor.execute(
                """SELECT * FROM appointments 
                   ORDER BY appointment_date DESC, appointment_time DESC, created_at DESC"""
            )
        else:
            cursor.execute(
                """SELECT * FROM appointments 
                   WHERE status = %s 
                   ORDER BY appointment_date DESC, appointment_time DESC, created_at DESC""",
                (status_filter,)
            )
        
        appointments_list = cursor.fetchall()
        cursor.close()
        conn.close()
    
    # Pass today's date for template comparison
    today_date = date.today()
    return render_template('appointments.html', 
                         appointments=appointments_list,
                         status_filter=status_filter,
                         today=today_date)


@app.route('/approve-appointment/<int:appointment_id>')
@login_required
def approve_appointment(appointment_id):
    """
    Admin route to approve an appointment request.
    Updates appointment status to APPROVED.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE appointments SET status = 'APPROVED' WHERE appointment_id = %s",
                (appointment_id,)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Appointment approved successfully!', 'success')
        except Error as e:
            flash(f'Error approving appointment: {str(e)}', 'error')
    
    return redirect(url_for('appointments'))


@app.route('/reject-appointment/<int:appointment_id>')
@login_required
def reject_appointment(appointment_id):
    """
    Admin route to reject an appointment request.
    Updates appointment status to REJECTED.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE appointments SET status = 'REJECTED' WHERE appointment_id = %s",
                (appointment_id,)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Appointment rejected.', 'info')
        except Error as e:
            flash(f'Error rejecting appointment: {str(e)}', 'error')
    
    return redirect(url_for('appointments'))


@app.route('/convert-appointment/<int:appointment_id>')
@login_required
def convert_appointment(appointment_id):
    """
    Convert an approved appointment into a visitor entry.
    Only approved appointments can be converted.
    Creates a visitor record with status INSIDE and links appointment_id.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check if appointment exists and is approved
            cursor.execute(
                "SELECT * FROM appointments WHERE appointment_id = %s AND status = 'APPROVED'",
                (appointment_id,)
            )
            appointment = cursor.fetchone()
            
            if not appointment:
                flash('Appointment not found or not approved. Only approved appointments can be converted.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('appointments'))
            
            # Check if appointment date is today or in the past
            appt_date = appointment['appointment_date']
            if appt_date > date.today():
                flash('Cannot convert appointment. Appointment date is in the future.', 'error')
                cursor.close()
                conn.close()
                return redirect(url_for('appointments'))
            
            # Check if already converted (optional: prevent duplicate conversion)
            cursor.execute(
                "SELECT * FROM visitors WHERE appointment_id = %s",
                (appointment_id,)
            )
            existing_visitor = cursor.fetchone()
            
            if existing_visitor:
                flash('This appointment has already been converted to a visitor entry.', 'warning')
                cursor.close()
                conn.close()
                return redirect(url_for('appointments'))
            
            # Convert appointment to visitor
            # Note: ID proof is required for visitors, so we use a default value
            # In production, you might want to collect ID proof during appointment booking
            id_proof = f"Appointment-{appointment_id}"  # Placeholder ID proof
            
            # Combine appointment date and time for check-in
            check_in_datetime = datetime.combine(appointment['appointment_date'], appointment['appointment_time'])
            
            cursor.execute(
                """INSERT INTO visitors (name, contact, id_proof, purpose, person_to_meet, 
                   check_in_time, status, appointment_id) 
                   VALUES (%s, %s, %s, %s, %s, %s, 'INSIDE', %s)""",
                (appointment['visitor_name'], appointment['contact'], id_proof, 
                 appointment['purpose'], appointment['person_to_meet'], 
                 check_in_datetime, appointment_id)
            )
            conn.commit()
            visitor_id = cursor.lastrowid
            cursor.close()
            conn.close()
            
            flash(f'Appointment converted successfully! Visitor ID: {visitor_id}', 'success')
        except Error as e:
            flash(f'Error converting appointment: {str(e)}', 'error')
    
    return redirect(url_for('appointments'))


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('error.html', error_code=404, 
                         error_message='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return render_template('error.html', error_code=500, 
                         error_message='Internal server error'), 500


# ==================== MAIN ====================

if __name__ == '__main__':
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)

