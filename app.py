"""
Visitor Management System
A secure, automated digital system to replace traditional manual visitor registers.

Future Enhancements (mentioned for viva):
- QR code passes for visitors
- SMS notifications for check-in/check-out
- Biometric verification
- Email notifications
- Visitor photo capture
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
    Initialize database with default admin if not exists.
    Creates admin user with username: admin, password: admin123
    """
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            # Check if admin exists
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
            
            cursor.close()
            conn.close()
    except Error as e:
        print(f"Error initializing database: {e}")


# Initialize database on startup
init_database()


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/')
def index():
    """Redirect to login page"""
    return redirect(url_for('login'))


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

