#!/usr/bin/env python3
"""
GFA School Management System
A comprehensive web-based system for JSS and SSS
Features: Student Registration, Result Processing, Subject Allocation, 
Fee Management, Report Card Generation
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, date
import os
import json
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas


app = Flask(__name__)
app.jinja_env.globals['now'] = datetime.now
app.config['SECRET_KEY'] = 'gfa-school-management-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///gfa_school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============================================================
# GRADING SYSTEM (Based on WAEC/Nigerian Standard)
# ============================================================

GRADING_SYSTEM = {
    'A1': {'min': 75, 'max': 100, 'point': 5.0, 'remark': 'Excellent'},
    'B2': {'min': 70, 'max': 74, 'point': 4.5, 'remark': 'Very Good'},
    'B3': {'min': 65, 'max': 69, 'point': 4.0, 'remark': 'Good'},
    'C4': {'min': 60, 'max': 64, 'point': 3.75, 'remark': 'Credit'},
    'C5': {'min': 55, 'max': 59, 'point': 3.25, 'remark': 'Credit'},
    'C6': {'min': 50, 'max': 54, 'point': 3.0, 'remark': 'Credit'},
    'D7': {'min': 45, 'max': 49, 'point': 2.0, 'remark': 'Pass'},
    'E8': {'min': 40, 'max': 44, 'point': 1.0, 'remark': 'Pass'},
    'F9': {'min': 0, 'max': 39, 'point': 0.0, 'remark': 'Fail'}
}

PSYCHOMOTOR_SCALE = {
    5: 'Excellent',
    4: 'Good',
    3: 'Fair',
    2: 'Poor',
    1: 'Very Poor'
}

SUBJECTS_JSS = [
    'Religious and Moral Instructions', 'Computer Study', 'Business Study',
    'Cultural and Creative Arts/Music', 'Basic Technology', 'Civic Education',
    'Yoruba Language', 'English Language', 'Mathematics', 'Basic Science',
    'Prevocational Studies', 'National Values Education', 'Physical Education',
    'French', 'Christian Religious Knowledge'
]

SUBJECTS_SSS_SCIENCE = [
    'Physics', 'Chemistry', 'Biology', 'Mathematics', 'English Language',
    'Animal Husbandry', 'Data Processing', 'Yoruba Language', 'Agricultural Science',
    'Civic Education', 'Geography', 'Economics', 'Further Mathematics',
    'Religious and Moral Instructions'
]

SUBJECTS_SSS_COMMERCIAL = [
    'Financial Accounting', 'Commerce', 'Economics', 'Geography', 'Government',
    'Agricultural Science', 'Biology', 'Yoruba Language', 'English Language',
    'Mathematics', 'Further Mathematics', 'Religious and Moral Instructions',
    'Civic Education'
]

SUBJECTS_SSS_ARTS = [
    'Literature-in-English', 'Christian Religious Knowledge', 'Government',
    'Biology', 'French', 'Economics', 'Religious and Moral Instructions',
    'Mathematics', 'English Language', 'Further Mathematics', 'Civic Education',
    'Data Processing', 'Animal Husbandry', 'Yoruba Language'
]

# ============================================================
# DATABASE MODELS
# ============================================================

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)  # admin, principal, teacher, bursar, student, parent
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def is_authenticated(self):
        return True
    def is_active(self):
        return self.is_active
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), unique=True)
    description = db.Column(db.Text)
    head_of_department = db.Column(db.Integer, db.ForeignKey('staff.id'))

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    staff_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    other_names = db.Column(db.String(50))
    sex = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    qualification = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    designation = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    date_employed = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department', foreign_keys=[department_id])
    user = db.relationship('User', foreign_keys=[user_id])

class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    level = db.Column(db.String(10), nullable=False)  # JSS or SSS
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    class_teacher_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    capacity = db.Column(db.Integer, default=40)
    room = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    department = db.relationship('Department')
    class_teacher = db.relationship('Staff', foreign_keys=[class_teacher_id])

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    admission_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    other_names = db.Column(db.String(50))
    sex = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)
    place_of_birth = db.Column(db.String(100))
    state_of_origin = db.Column(db.String(50))
    local_government = db.Column(db.String(50))
    nationality = db.Column(db.String(50), default='Nigerian')
    religion = db.Column(db.String(30))
    blood_group = db.Column(db.String(5))
    genotype = db.Column(db.String(5))
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    parent_email = db.Column(db.String(100))
    parent_address = db.Column(db.Text)
    parent_occupation = db.Column(db.String(50))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    date_admitted = db.Column(db.Date)
    previous_school = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student_class = db.relationship('Class', foreign_keys=[class_id])
    department = db.relationship('Department')
    user = db.relationship('User')

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True)
    category = db.Column(db.String(30))  # Core, Elective, Vocational
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

class Session(db.Model):
    __tablename__ = 'sessions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Term(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    term_number = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(50))

class ClassSubject(db.Model):
    __tablename__ = 'class_subjects'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    is_compulsory = db.Column(db.Boolean, default=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    class_obj = db.relationship('Class', foreign_keys=[class_id])
    subject = db.relationship('Subject', foreign_keys=[subject_id])
    department = db.relationship('Department', foreign_keys=[department_id])
    teacher = db.relationship('Staff', foreign_keys=[teacher_id])
    session = db.relationship('Session', foreign_keys=[session_id])

class StudentSubject(db.Model):
    __tablename__ = 'student_subjects'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    is_active = db.Column(db.Boolean, default=True)
    enrolled_date = db.Column(db.Date, default=date.today)
    student = db.relationship('Student', foreign_keys=[student_id])
    subject = db.relationship('Subject', foreign_keys=[subject_id])
    class_obj = db.relationship('Class', foreign_keys=[class_id])
    session = db.relationship('Session', foreign_keys=[session_id])

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    school_opened = db.Column(db.Integer, default=0)
    times_present = db.Column(db.Integer, default=0)
    times_absent = db.Column(db.Integer, default=0)
    times_late = db.Column(db.Integer, default=0)
    vacates_on = db.Column(db.Date)
    resumes_on = db.Column(db.Date)
    updated_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', foreign_keys=[student_id])
    student = db.relationship('Student', foreign_keys=[student_id])
    session = db.relationship('Session', foreign_keys=[session_id])
    term = db.relationship('Term', foreign_keys=[term_id])

class TermResult(db.Model):
    __tablename__ = 'term_results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    ca_score = db.Column(db.Integer)
    exam_score = db.Column(db.Integer)
    total_score = db.Column(db.Integer)
    grade = db.Column(db.String(5))
    grade_point = db.Column(db.Numeric(3, 2))
    remark = db.Column(db.String(20))
    subject_position = db.Column(db.Integer)
    entered_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    entered_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    verified_at = db.Column(db.DateTime)
    student = db.relationship('Student', foreign_keys=[student_id])
    subject = db.relationship('Subject', foreign_keys=[subject_id])
    session = db.relationship('Session', foreign_keys=[session_id])
    term = db.relationship('Term', foreign_keys=[term_id])
    student = db.relationship('Student', foreign_keys=[student_id])
    subject = db.relationship('Subject', foreign_keys=[subject_id])
    session = db.relationship('Session', foreign_keys=[session_id])
    term = db.relationship('Term', foreign_keys=[term_id])


class SessionResult(db.Model):
    __tablename__ = 'session_results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    first_term_total = db.Column(db.Integer)
    first_term_avg = db.Column(db.Numeric(5, 2))
    first_term_grade = db.Column(db.String(5))
    second_term_total = db.Column(db.Integer)
    second_term_avg = db.Column(db.Numeric(5, 2))
    second_term_grade = db.Column(db.String(5))
    third_term_total = db.Column(db.Integer)
    third_term_avg = db.Column(db.Numeric(5, 2))
    third_term_grade = db.Column(db.String(5))
    sessional_total = db.Column(db.Integer)
    sessional_avg = db.Column(db.Numeric(5, 2))
    sessional_grade = db.Column(db.String(5))
    sessional_position = db.Column(db.Integer)
    class_highest = db.Column(db.Numeric(5, 2))
    class_lowest = db.Column(db.Numeric(5, 2))
    class_average = db.Column(db.Numeric(5, 2))
    year_highest = db.Column(db.Numeric(5, 2))
    year_lowest = db.Column(db.Numeric(5, 2))
    year_average = db.Column(db.Numeric(5, 2))
    year_position = db.Column(db.Integer)
    total_obtainable = db.Column(db.Integer)
    total_score = db.Column(db.Integer)
    grade_point = db.Column(db.Numeric(3, 2))
    promoted_to = db.Column(db.Integer, db.ForeignKey('classes.id'))
    promotion_status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', foreign_keys=[student_id])
    student = db.relationship('Student', foreign_keys=[student_id])

class PsychomotorAssessment(db.Model):
    __tablename__ = 'psychomotor_assessments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    handwriting = db.Column(db.Integer)
    verbal_fluency = db.Column(db.Integer)
    sports = db.Column(db.Integer)
    handling_tools = db.Column(db.Integer)
    drawing_painting = db.Column(db.Integer)
    musical_skills = db.Column(db.Integer)
    assessed_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', foreign_keys=[student_id])
    student = db.relationship('Student', foreign_keys=[student_id])
    session = db.relationship('Session', foreign_keys=[session_id])
    term = db.relationship('Term', foreign_keys=[term_id])

class AffectiveAssessment(db.Model):
    __tablename__ = 'affective_assessments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    punctuality = db.Column(db.Integer)
    neatness = db.Column(db.Integer)
    politeness = db.Column(db.Integer)
    attitude_to_work = db.Column(db.Integer)
    attentiveness = db.Column(db.Integer)
    speaking_handwriting = db.Column(db.Integer)
    assessed_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    assessed_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', foreign_keys=[student_id])
    student = db.relationship('Student', foreign_keys=[student_id])
    session = db.relationship('Session', foreign_keys=[session_id])
    term = db.relationship('Term', foreign_keys=[term_id])

class ResultComment(db.Model):
    __tablename__ = 'result_comments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    class_teacher_comment = db.Column(db.Text)
    principal_comment = db.Column(db.Text)
    achievement_box = db.Column(db.Text)
    class_teacher_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    principal_id = db.Column(db.Integer, db.ForeignKey('staff.id'))
    teacher_signed_at = db.Column(db.DateTime)
    principal_signed_at = db.Column(db.DateTime)
    student = db.relationship('Student', foreign_keys=[student_id])
    student = db.relationship('Student', foreign_keys=[student_id])
    session = db.relationship('Session', foreign_keys=[session_id])
    term = db.relationship('Term', foreign_keys=[term_id])

class SchoolFee(db.Model):
    __tablename__ = 'school_fees'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    fee_type = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    is_mandatory = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    class_obj = db.relationship('Class', foreign_keys=[class_id])
    department = db.relationship('Department', foreign_keys=[department_id])
    session = db.relationship('Session', foreign_keys=[session_id])
    term = db.relationship('Term', foreign_keys=[term_id])
    class_obj = db.relationship('Class', foreign_keys=[class_id])
    department = db.relationship('Department', foreign_keys=[department_id])
    session = db.relationship('Session', foreign_keys=[session_id])
    term = db.relationship('Term', foreign_keys=[term_id])

class FeePayment(db.Model):
    __tablename__ = 'fee_payments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    fee_id = db.Column(db.Integer, db.ForeignKey('school_fees.id'))
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False)
    amount_due = db.Column(db.Numeric(10, 2))
    balance = db.Column(db.Numeric(10, 2))
    payment_method = db.Column(db.String(30))
    transaction_reference = db.Column(db.String(100))
    payment_date = db.Column(db.Date, default=date.today)
    received_by = db.Column(db.Integer, db.ForeignKey('staff.id'))
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship('Student', foreign_keys=[student_id])
    fee = db.relationship('SchoolFee', foreign_keys=[fee_id])
    student = db.relationship('Student', foreign_keys=[student_id])
    fee = db.relationship('SchoolFee', foreign_keys=[fee_id])

class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    school_name = db.Column(db.String(255), default='GFA Secondary School')
    school_address = db.Column(db.Text)
    school_phone = db.Column(db.String(50))
    school_email = db.Column(db.String(100))
    school_motto = db.Column(db.Text)
    current_session = db.Column(db.String(20))
    current_term = db.Column(db.Integer)
    ca_max_score = db.Column(db.Integer, default=30)
    exam_max_score = db.Column(db.Integer, default=70)
    pass_mark = db.Column(db.Integer, default=40)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_grade(total_score):
    """Calculate grade based on total score using Nigerian grading system"""
    if total_score is None:
        return None, None, None
    for grade, details in GRADING_SYSTEM.items():
        if details['min'] <= total_score <= details['max']:
            return grade, float(details['point']), details['remark']
    return 'F9', 0.0, 'Fail'

def get_subjects_for_class(class_name, department=None):
    """Get subjects based on class and department"""
    if 'JSS' in class_name:
        return SUBJECTS_JSS
    elif 'SSS' in class_name:
        if department == 'Science':
            return SUBJECTS_SSS_SCIENCE
        elif department == 'Commercial':
            return SUBJECTS_SSS_COMMERCIAL
        elif department == 'Arts':
            return SUBJECTS_SSS_ARTS
    return []

def role_required(roles):
    """Decorator to check user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('Access denied. Insufficient permissions.', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============================================================
# ROUTES - AUTHENTICATION
# ============================================================
@app.template_filter('ordinal')
def ordinal_filter(n):
    if n is None:
        return 'N/A'
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_students': Student.query.count(),
        'total_staff': Staff.query.count(),
        'total_classes': Class.query.filter_by(is_active=True).count(),
        'total_subjects': Subject.query.filter_by(is_active=True).count(),
        'active_sessions': Session.query.filter_by(is_active=True).count()
    }

    recent_students = Student.query.order_by(Student.created_at.desc()).limit(5).all()

    return render_template('dashboard.html', stats=stats, recent_students=recent_students)

# ============================================================
# ROUTES - STUDENT MANAGEMENT
# ============================================================

@app.route('/students')
@login_required
def students_list():
    page = request.args.get('page', 1, type=int)
    class_filter = request.args.get('class', '')
    status_filter = request.args.get('status', '')

    query = Student.query
    if class_filter:
        query = query.filter_by(class_id=class_filter)
    if status_filter:
        query = query.filter_by(status=status_filter)

    students = query.order_by(Student.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    classes = Class.query.filter_by(is_active=True).all()

    return render_template('students/list.html', students=students, classes=classes)

@app.route('/students/register', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal'])
def student_register():
    if request.method == 'POST':
        # Generate admission number
        year = datetime.now().year
        count = Student.query.filter(
            db.extract('year', Student.created_at) == year
        ).count() + 1
        admission_number = f"GFA/{year}/{count:04d}"

        student = Student(
            admission_number=admission_number,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            other_names=request.form.get('other_names'),
            sex=request.form.get('sex'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None,
            state_of_origin=request.form.get('state_of_origin'),
            local_government=request.form.get('local_government'),
            religion=request.form.get('religion'),
            address=request.form.get('address'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            parent_name=request.form.get('parent_name'),
            parent_phone=request.form.get('parent_phone'),
            parent_email=request.form.get('parent_email'),
            parent_address=request.form.get('parent_address'),
            parent_occupation=request.form.get('parent_occupation'),
            class_id=request.form.get('class_id'),
            department_id=request.form.get('department_id'),
            date_admitted=date.today(),
            previous_school=request.form.get('previous_school')
        )

        db.session.add(student)
        db.session.commit()

        flash(f'Student registered successfully! Admission Number: {admission_number}', 'success')
        return redirect(url_for('students_list'))

    classes = Class.query.filter_by(is_active=True).all()
    departments = Department.query.all()
    return render_template('students/register.html', classes=classes, departments=departments)

@app.route('/students/<int:student_id>')
@login_required
def student_profile(student_id):
    student = Student.query.get_or_404(student_id)

    # Get academic history
    term_results = TermResult.query.filter_by(student_id=student_id).order_by(
        TermResult.session_id.desc(), TermResult.term_id.desc()
    ).all()

    # Get fee history
    fee_payments = FeePayment.query.filter_by(student_id=student_id).order_by(
        FeePayment.payment_date.desc()
    ).all()

    # Calculate fee balance
    total_paid = db.session.query(db.func.sum(FeePayment.amount_paid)).filter_by(
        student_id=student_id
    ).scalar() or 0

    total_due = db.session.query(db.func.sum(SchoolFee.amount)).join(
        FeePayment, FeePayment.fee_id == SchoolFee.id
    ).filter(FeePayment.student_id == student_id).scalar() or 0

    return render_template('students/profile.html', 
                         student=student, 
                         term_results=term_results,
                         fee_payments=fee_payments,
                         total_paid=total_paid,
                         total_due=total_due)

@app.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal'])
def student_edit(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        student.first_name = request.form.get('first_name')
        student.last_name = request.form.get('last_name')
        student.other_names = request.form.get('other_names')
        student.sex = request.form.get('sex')
        student.class_id = request.form.get('class_id')
        student.department_id = request.form.get('department_id')
        student.status = request.form.get('status')
        student.address = request.form.get('address')
        student.phone = request.form.get('phone')
        student.parent_name = request.form.get('parent_name')
        student.parent_phone = request.form.get('parent_phone')

        db.session.commit()
        flash('Student information updated successfully!', 'success')
        return redirect(url_for('student_profile', student_id=student.id))

    classes = Class.query.filter_by(is_active=True).all()
    departments = Department.query.all()
    return render_template('students/edit.html', student=student, classes=classes, departments=departments)

# ============================================================
# ROUTES - RESULT PROCESSING
# ============================================================

@app.route('/results/entry', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal', 'teacher'])
def result_entry():
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        subject_id = request.form.get('subject_id')
        session_id = request.form.get('session_id')
        term_id = request.form.get('term_id')

        students = Student.query.filter_by(class_id=class_id, status='active').all()

        for student in students:
            ca = request.form.get(f'ca_{student.id}')
            exam = request.form.get(f'exam_{student.id}')

            if ca and exam:
                ca = int(ca)
                exam = int(exam)
                total = ca + exam
                grade, point, remark = calculate_grade(total)

                result = TermResult.query.filter_by(
                    student_id=student.id,
                    subject_id=subject_id,
                    session_id=session_id,
                    term_id=term_id
                ).first()

                if result:
                    result.ca_score = ca
                    result.exam_score = exam
                    result.total_score = total
                    result.grade = grade
                    result.grade_point = point
                    result.remark = remark
                    result.entered_by = current_user.id
                else:
                    result = TermResult(
                        student_id=student.id,
                        subject_id=subject_id,
                        class_id=class_id,
                        session_id=session_id,
                        term_id=term_id,
                        ca_score=ca,
                        exam_score=exam,
                        total_score=total,
                        grade=grade,
                        grade_point=point,
                        remark=remark,
                        entered_by=current_user.id
                    )
                    db.session.add(result)

        db.session.commit()
        flash('Results entered successfully!', 'success')
        return redirect(url_for('result_entry'))

    classes = Class.query.filter_by(is_active=True).all()
    subjects = Subject.query.filter_by(is_active=True).all()
    sessions = Session.query.all()
    terms = Term.query.all()

    return render_template('results/entry.html', 
                         classes=classes, subjects=subjects, 
                         sessions=sessions, terms=terms)

@app.route('/results/view')
@login_required
def results_view():
    student_id = request.args.get('student_id')
    class_id = request.args.get('class_id')
    session_id = request.args.get('session_id')
    term_id = request.args.get('term_id')

    query = TermResult.query
    if student_id:
        query = query.filter_by(student_id=student_id)
    if class_id:
        query = query.filter_by(class_id=class_id)
    if session_id:
        query = query.filter_by(session_id=session_id)
    if term_id:
        query = query.filter_by(term_id=term_id)

    results = query.order_by(TermResult.student_id, TermResult.subject_id).all()

    students = Student.query.filter_by(status='active').all()
    classes = Class.query.filter_by(is_active=True).all()
    sessions = Session.query.all()
    terms = Term.query.all()

    return render_template('results/view.html', 
                         results=results, students=students,
                         classes=classes, sessions=sessions, terms=terms)

@app.route('/results/calculate-positions', methods=['POST'])
@login_required
@role_required(['admin', 'principal'])
def calculate_positions():
    class_id = request.form.get('class_id')
    session_id = request.form.get('session_id')
    term_id = request.form.get('term_id')

    if not all([class_id, session_id, term_id]):
        flash('Please select class, session, and term.', 'danger')
        return redirect(url_for('results_view'))

    # ============================================================
    # 1. CALCULATE SUBJECT POSITIONS
    # ============================================================
    
    # Get only subjects that have results for this class/session/term
    subject_ids = db.session.query(TermResult.subject_id).filter_by(
        class_id=class_id,
        session_id=session_id,
        term_id=term_id
    ).distinct().all()
    
    subject_ids = [s[0] for s in subject_ids]

    for subject_id in subject_ids:
        results = TermResult.query.filter_by(
            class_id=class_id,
            subject_id=subject_id,
            session_id=session_id,
            term_id=term_id
        ).order_by(TermResult.total_score.desc()).all()

        # Handle ties: same score = same position
        current_position = 1
        previous_score = None
        skip_count = 0
        
        for i, result in enumerate(results, 1):
            if result.total_score != previous_score:
                current_position = i - skip_count
                previous_score = result.total_score
            else:
                skip_count += 1
            
            result.subject_position = current_position

    # ============================================================
    # 2. CALCULATE OVERALL CLASS POSITIONS & STATISTICS
    # ============================================================
    
    # Get all students with results in this class/session/term
    student_ids = db.session.query(TermResult.student_id).filter_by(
        class_id=class_id,
        session_id=session_id,
        term_id=term_id
    ).distinct().all()
    
    student_ids = [s[0] for s in student_ids]

    student_averages = []
    
    for student_id in student_ids:
        results = TermResult.query.filter_by(
            student_id=student_id,
            class_id=class_id,
            session_id=session_id,
            term_id=term_id
        ).all()
        
        if results:
            total_score = sum(r.total_score for r in results)
            avg_score = total_score / len(results)
            student_averages.append({
                'student_id': student_id,
                'total_score': total_score,
                'avg_score': avg_score,
                'num_subjects': len(results)
            })
    
    # Sort by average score descending
    student_averages.sort(key=lambda x: x['avg_score'], reverse=True)
    
    # Calculate class-wide statistics
    if student_averages:
        all_avgs = [s['avg_score'] for s in student_averages]
        class_highest = max(all_avgs)
        class_lowest = min(all_avgs)
        class_avg = sum(all_avgs) / len(all_avgs)
    else:
        class_highest = class_lowest = class_avg = 0

    # Handle ties for overall positions and update SessionResult
    overall_position = 1
    previous_avg = None
    skip_count = 0
    
    for i, student_data in enumerate(student_averages, 1):
        if student_data['avg_score'] != previous_avg:
            overall_position = i - skip_count
            previous_avg = student_data['avg_score']
        else:
            skip_count += 1
        
        # Update or create SessionResult
        session_result = SessionResult.query.filter_by(
            student_id=student_data['student_id'],
            class_id=class_id,
            session_id=session_id
        ).first()
        
        if not session_result:
            session_result = SessionResult(
                student_id=student_data['student_id'],
                class_id=class_id,
                session_id=session_id
            )
            db.session.add(session_result)
        
        # Store all the data that the report card needs
        session_result.sessional_avg = student_data['avg_score']
        session_result.total_score = student_data['total_score']
        session_result.total_obtainable = student_data['num_subjects'] * 100
        session_result.class_highest = class_highest
        session_result.class_lowest = class_lowest
        session_result.class_average = class_avg
        # Store overall position in session_position (reuse existing column)
        session_result.sessional_position = overall_position

    db.session.commit()
    flash('Positions and class statistics calculated successfully!', 'success')
    return redirect(url_for('results_view'))

@app.route('/results/session-aggregate', methods=['POST'])
@login_required
@role_required(['admin', 'principal'])
def session_aggregate():
    student_id = request.form.get('student_id')
    session_id = request.form.get('session_id')

    student = Student.query.get(student_id)

    # Get all term results for the session
    for term_num in [1, 2, 3]:
        term_results = TermResult.query.filter_by(
            student_id=student_id,
            session_id=session_id,
            term_id=term_num
        ).all()

        if term_results:
            total = sum(r.total_score for r in term_results)
            avg = total / len(term_results)
            grade, point, remark = calculate_grade(avg)

            if term_num == 1:
                first_term_total = total
                first_term_avg = avg
                first_term_grade = grade
            elif term_num == 2:
                second_term_total = total
                second_term_avg = avg
                second_term_grade = grade
            elif term_num == 3:
                third_term_total = total
                third_term_avg = avg
                third_term_grade = grade

    # Calculate sessional aggregate
    sessional_total = (first_term_total or 0) + (second_term_total or 0) + (third_term_total or 0)
    sessional_avg = sessional_total / 3 if sessional_total > 0 else 0
    sessional_grade, sessional_point, _ = calculate_grade(sessional_avg)

    session_result = SessionResult.query.filter_by(
        student_id=student_id, session_id=session_id
    ).first()

    if not session_result:
        session_result = SessionResult(
            student_id=student_id,
            class_id=student.class_id,
            session_id=session_id
        )
        db.session.add(session_result)

    session_result.first_term_total = first_term_total
    session_result.first_term_avg = first_term_avg
    session_result.first_term_grade = first_term_grade
    session_result.second_term_total = second_term_total
    session_result.second_term_avg = second_term_avg
    session_result.second_term_grade = second_term_grade
    session_result.third_term_total = third_term_total
    session_result.third_term_avg = third_term_avg
    session_result.third_term_grade = third_term_grade
    session_result.sessional_total = sessional_total
    session_result.sessional_avg = sessional_avg
    session_result.sessional_grade = sessional_grade

    db.session.commit()
    flash('Session results aggregated successfully!', 'success')
    return redirect(url_for('results_view'))

# ============================================================
# ROUTES - PSYCHOMOTOR & AFFECTIVE ASSESSMENTS
# ============================================================

@app.route('/assessments/psychomotor', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal', 'teacher'])
def psychomotor_assessment():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        session_id = request.form.get('session_id')
        term_id = request.form.get('term_id')

        assessment = PsychomotorAssessment.query.filter_by(
            student_id=student_id, session_id=session_id, term_id=term_id
        ).first()

        if not assessment:
            assessment = PsychomotorAssessment(
                student_id=student_id,
                session_id=session_id,
                term_id=term_id
            )
            db.session.add(assessment)

        assessment.handwriting = int(request.form.get('handwriting', 3))
        assessment.verbal_fluency = int(request.form.get('verbal_fluency', 3))
        assessment.sports = int(request.form.get('sports', 3))
        assessment.handling_tools = int(request.form.get('handling_tools', 3))
        assessment.drawing_painting = int(request.form.get('drawing_painting', 3))
        assessment.musical_skills = int(request.form.get('musical_skills', 3))
        assessment.assessed_by = current_user.id

        db.session.commit()
        flash('Psychomotor assessment saved!', 'success')
        return redirect(url_for('psychomotor_assessment'))

    students = Student.query.filter_by(status='active').all()
    sessions = Session.query.all()
    terms = Term.query.all()

    return render_template('assessments/psychomotor.html', 
                         students=students, sessions=sessions, terms=terms,
                         scale=PSYCHOMOTOR_SCALE)

@app.route('/assessments/affective', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal', 'teacher'])
def affective_assessment():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        session_id = request.form.get('session_id')
        term_id = request.form.get('term_id')

        assessment = AffectiveAssessment.query.filter_by(
            student_id=student_id, session_id=session_id, term_id=term_id
        ).first()

        if not assessment:
            assessment = AffectiveAssessment(
                student_id=student_id,
                session_id=session_id,
                term_id=term_id
            )
            db.session.add(assessment)

        assessment.punctuality = int(request.form.get('punctuality', 3))
        assessment.neatness = int(request.form.get('neatness', 3))
        assessment.politeness = int(request.form.get('politeness', 3))
        assessment.attitude_to_work = int(request.form.get('attitude_to_work', 3))
        assessment.attentiveness = int(request.form.get('attentiveness', 3))
        assessment.speaking_handwriting = int(request.form.get('speaking_handwriting', 3))
        assessment.assessed_by = current_user.id

        db.session.commit()
        flash('Affective assessment saved!', 'success')
        return redirect(url_for('affective_assessment'))

    students = Student.query.filter_by(status='active').all()
    sessions = Session.query.all()
    terms = Term.query.all()

    return render_template('assessments/affective.html',
                         students=students, sessions=sessions, terms=terms,
                         scale=PSYCHOMOTOR_SCALE)

# ============================================================
# ROUTES - REPORT CARD GENERATION
# ============================================================

@app.route('/report-card/<int:student_id>')
@login_required
def report_card(student_id):
    student = Student.query.get_or_404(student_id)
    session_id = request.args.get('session_id')
    term_id = request.args.get('term_id')

    if not session_id or not term_id:
        flash('Please select session and term.', 'warning')
        return redirect(url_for('results_view'))

    # Get term results
    term_results = TermResult.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).all()

    # Get attendance
    attendance = Attendance.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).first()

    # Get psychomotor
    psychomotor = PsychomotorAssessment.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).first()

    # Get affective
    affective = AffectiveAssessment.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).first()

    # Get comments
    comments = ResultComment.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).first()

    # ============================================================
    # CALCULATE STUDENT'S OWN STATS
    # ============================================================
    if term_results:
        total_score = sum(r.total_score for r in term_results)
        total_obtainable = len(term_results) * 100
        student_avg = total_score / len(term_results)
        grade, point, remark = calculate_grade(student_avg)
    else:
        total_score = 0
        total_obtainable = 0
        student_avg = 0
        grade = 'N/A'
        point = 0
        remark = 'N/A'

    # ============================================================
    # CALCULATE CLASS STATISTICS (all students in same class)
    # ============================================================
    class_id = student.class_id
    
    # Get all students in this class with results
    class_student_ids = db.session.query(TermResult.student_id).filter_by(
        class_id=class_id,
        session_id=session_id,
        term_id=term_id
    ).distinct().all()
    class_student_ids = [s[0] for s in class_student_ids]

    class_averages = []
    for sid in class_student_ids:
        results = TermResult.query.filter_by(
            student_id=sid,
            class_id=class_id,
            session_id=session_id,
            term_id=term_id
        ).all()
        if results:
            avg = sum(r.total_score for r in results) / len(results)
            class_averages.append({'student_id': sid, 'avg': avg})

    # Sort to find position
    class_averages.sort(key=lambda x: x['avg'], reverse=True)
    
    # Find this student's position
    class_position = None
    for i, ca in enumerate(class_averages, 1):
        if ca['student_id'] == student_id:
            class_position = i
            break

    # Class stats
    if class_averages:
        all_avgs = [ca['avg'] for ca in class_averages]
        class_average = sum(all_avgs) / len(all_avgs)
        class_highest = max(all_avgs)
        class_lowest = min(all_avgs)
    else:
        class_average = class_highest = class_lowest = 0

    # ============================================================
    # CALCULATE YEAR/LEVEL STATISTICS (all students in JSS or SSS)
    # ============================================================
    student_class = Class.query.get(class_id)
    if student_class:
        # Get all classes in same level (JSS or SSS)
        year_classes = Class.query.filter_by(
            level=student_class.level,
            is_active=True
        ).all()
        year_class_ids = [c.id for c in year_classes]

        year_student_ids = db.session.query(TermResult.student_id).filter(
            TermResult.class_id.in_(year_class_ids),
            TermResult.session_id == session_id,
            TermResult.term_id == term_id
        ).distinct().all()
        year_student_ids = [s[0] for s in year_student_ids]

        year_averages = []
        for sid in year_student_ids:
            results = TermResult.query.filter_by(
                student_id=sid,
                session_id=session_id,
                term_id=term_id
            ).all()
            if results:
                avg = sum(r.total_score for r in results) / len(results)
                year_averages.append({'student_id': sid, 'avg': avg})

        year_averages.sort(key=lambda x: x['avg'], reverse=True)
        
        year_position = None
        for i, ya in enumerate(year_averages, 1):
            if ya['student_id'] == student_id:
                year_position = i
                break
        
        if year_averages:
            all_year_avgs = [ya['avg'] for ya in year_averages]
            year_average = sum(all_year_avgs) / len(all_year_avgs)
            year_highest = max(all_year_avgs)
            year_lowest = min(all_year_avgs)
        else:
            year_average = year_highest = year_lowest = 0
            year_position = None
    else:
        year_average = year_highest = year_lowest = 0
        year_position = None

    session = Session.query.get(session_id)
    term = Term.query.get(term_id)

    return render_template('reports/report_card.html',
                         student=student,
                         term_results=term_results,
                         attendance=attendance,
                         psychomotor=psychomotor,
                         affective=affective,
                         comments=comments,
                         total_score=total_score,
                         total_obtainable=total_obtainable,
                         student_avg=student_avg,
                         grade=grade,
                         point=point,
                         remark=remark,
                         class_average=class_average,
                         class_position=class_position,
                         class_highest=class_highest,
                         class_lowest=class_lowest,
                         year_position=year_position,
                         year_average=year_average,
                         year_highest=year_highest,
                         year_lowest=year_lowest,
                         session=session,
                         term=term,
                         grading_system=GRADING_SYSTEM,
                         psychomotor_scale=PSYCHOMOTOR_SCALE)

@app.route('/report-card/pdf/<int:student_id>')
@login_required
def report_card_pdf(student_id):
    student = Student.query.get_or_404(student_id)
    session_id = request.args.get('session_id')
    term_id = request.args.get('term_id')

    if not session_id or not term_id:
        flash('Please select session and term.', 'warning')
        return redirect(url_for('report_card', student_id=student_id))

    # Get term results
    term_results = TermResult.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).all()

    # Get attendance
    attendance = Attendance.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).first()

    # Get psychomotor
    psychomotor = PsychomotorAssessment.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).first()

    # Get affective
    affective = AffectiveAssessment.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).first()

    # Get comments
    comments = ResultComment.query.filter_by(
        student_id=student_id,
        session_id=session_id,
        term_id=term_id
    ).first()

    # Get school settings
    setting = Setting.query.first()
    school_name = setting.school_name if setting else 'SECONDARY SCHOOL'

    # Calculate student stats
    if term_results:
        total_score = sum(r.total_score for r in term_results)
        total_obtainable = len(term_results) * 100
        student_avg = total_score / len(term_results)
        grade, point, remark = calculate_grade(student_avg)
    else:
        total_score = 0
        total_obtainable = 0
        student_avg = 0
        grade = 'N/A'
        point = 0
        remark = 'N/A'

    # Calculate class statistics
    class_id = student.class_id
    class_student_ids = db.session.query(TermResult.student_id).filter_by(
        class_id=class_id,
        session_id=session_id,
        term_id=term_id
    ).distinct().all()
    class_student_ids = [s[0] for s in class_student_ids]

    class_averages = []
    for sid in class_student_ids:
        results = TermResult.query.filter_by(
            student_id=sid,
            class_id=class_id,
            session_id=session_id,
            term_id=term_id
        ).all()
        if results:
            avg = sum(r.total_score for r in results) / len(results)
            class_averages.append({'student_id': sid, 'avg': avg})

    class_averages.sort(key=lambda x: x['avg'], reverse=True)
    
    class_position = None
    for i, ca in enumerate(class_averages, 1):
        if ca['student_id'] == student_id:
            class_position = i
            break

    if class_averages:
        all_avgs = [ca['avg'] for ca in class_averages]
        class_average = sum(all_avgs) / len(all_avgs)
    else:
        class_average = 0

    session = Session.query.get(session_id)
    term = Term.query.get(term_id)

    # Generate PDF using ReportLab
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1*cm, bottomMargin=1*cm)
    elements = []
    styles = getSampleStyleSheet()

    # ============================================================
    # STYLES
    # ============================================================
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a5276'),
        alignment=1,  # Center
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    subheader_style = ParagraphStyle(
        'CustomSubHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#1a5276'),
        alignment=1,
        spaceAfter=12
    )

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.black
    )

    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black
    )

    # ============================================================
    # HEADER
    # ============================================================
    elements.append(Paragraph(school_name.upper(), header_style))
    elements.append(Paragraph("Student Academic Report Card", subheader_style))
    if setting and setting.school_motto:
        elements.append(Paragraph(f"<i>{setting.school_motto}</i>", 
                                  ParagraphStyle('Motto', parent=normal_style, alignment=1, fontSize=8)))
    elements.append(Spacer(1, 0.2*inch))

    # ============================================================
    # STUDENT INFO TABLE
    # ============================================================
    student_data = [
        [Paragraph('<b>Name:</b>', title_style), 
         Paragraph(f"{student.first_name} {student.last_name} {student.other_names or ''}", normal_style),
         Paragraph('<b>Admission No:</b>', title_style), 
         Paragraph(student.admission_number, normal_style)],
        [Paragraph('<b>Class:</b>', title_style), 
         Paragraph(student.student_class.name if student.student_class else 'N/A', normal_style),
         Paragraph('<b>Sex:</b>', title_style), 
         Paragraph(student.sex or 'N/A', normal_style)],
        [Paragraph('<b>Session:</b>', title_style), 
         Paragraph(session.name if session else 'N/A', normal_style),
         Paragraph('<b>Term:</b>', title_style), 
         Paragraph(term.name if term else 'N/A', normal_style)],
    ]

    student_table = Table(student_data, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 2.2*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eaf2f8')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#eaf2f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 0.2*inch))

    # ============================================================
    # ACADEMIC RESULTS TABLE
    # ============================================================
    if term_results:
        results_data = [['Subject', 'C.A (30)', 'Exam (70)', 'Total', 'Grade', 'Position', 'Remark']]
        for result in term_results:
            results_data.append([
                result.subject.name,
                str(result.ca_score or 0),
                str(result.exam_score or 0),
                str(result.total_score or 0),
                result.grade or 'N/A',
                str(result.subject_position or 'N/A'),
                result.remark or 'N/A'
            ])

        # Add summary row
        results_data.append([
            Paragraph('<b>TOTAL / AVERAGE</b>', title_style),
            '', '',
            Paragraph(f'<b>{total_score}</b>', title_style),
            Paragraph(f'<b>{grade}</b>', title_style),
            '',
            Paragraph(f'<b>{remark}</b>', title_style)
        ])

        results_table = Table(results_data, repeatRows=1)
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d5e8d4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, -1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(results_table)
        elements.append(Spacer(1, 0.2*inch))

    # ============================================================
    # SUMMARY STATISTICS TABLE
    # ============================================================
    summary_data = [
        [Paragraph('<b>Total Obtainable:</b>', title_style), str(total_obtainable),
         Paragraph('<b>Class Average:</b>', title_style), f"{class_average:.2f}%" if class_average else 'N/A'],
        [Paragraph('<b>Total Score:</b>', title_style), str(total_score),
         Paragraph('<b>Class Position:</b>', title_style), f"{class_position}{'' if class_position else ''}" if class_position else 'N/A'],
        [Paragraph('<b>Student Average:</b>', title_style), f"{student_avg:.2f}%",
         Paragraph('<b>Grade Point:</b>', title_style), str(point)],
        [Paragraph('<b>Grade:</b>', title_style), grade,
         Paragraph('<b>Remark:</b>', title_style), remark],
    ]

    summary_table = Table(summary_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eaf2f8')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#eaf2f8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2*inch))

    # ============================================================
    # PSYCHOMOTOR & AFFECTIVE ASSESSMENTS
    # ============================================================
    if psychomotor or affective:
        elements.append(Paragraph("<b>PSYCHOMOTOR & AFFECTIVE ASSESSMENT</b>", 
                                ParagraphStyle('SectionHeader', parent=title_style, 
                                              textColor=colors.HexColor('#1a5276'), 
                                              fontSize=11, spaceAfter=6)))

        # Psychomotor
        if psychomotor:
            psycho_data = [['Psychomotor Skills', 'Rating', 'Remarks']]
            psycho_items = [
                ('Handwriting', psychomotor.handwriting),
                ('Verbal Fluency', psychomotor.verbal_fluency),
                ('Sports', psychomotor.sports),
                ('Handling Tools', psychomotor.handling_tools),
                ('Drawing & Painting', psychomotor.drawing_painting),
                ('Musical Skills', psychomotor.musical_skills),
            ]
            for skill, rating in psycho_items:
                psycho_data.append([skill, str(rating or 'N/A'), PSYCHOMOTOR_SCALE.get(rating, 'N/A')])

        # Affective
        if affective:
            affect_data = [['Affective Disposition', 'Rating', 'Remarks']]
            affect_items = [
                ('Punctuality', affective.punctuality),
                ('Neatness', affective.neatness),
                ('Politeness', affective.politeness),
                ('Attitude to Work', affective.attitude_to_work),
                ('Attentiveness', affective.attentiveness),
                ('Speaking/Handwriting', affective.speaking_handwriting),
            ]
            for trait, rating in affect_items:
                affect_data.append([trait, str(rating or 'N/A'), PSYCHOMOTOR_SCALE.get(rating, 'N/A')])

        # Combine side by side if both exist
        if psychomotor and affective:
            max_rows = max(len(psycho_data), len(affect_data))
            combined = []
            for i in range(max_rows):
                p_row = psycho_data[i] if i < len(psycho_data) else ['', '', '']
                a_row = affect_data[i] if i < len(affect_data) else ['', '', '']
                combined.append(p_row + a_row)
            
            assess_table = Table(combined, colWidths=[1.5*inch, 0.8*inch, 1.2*inch, 1.5*inch, 0.8*inch, 1.2*inch])
        elif psychomotor:
            assess_table = Table(psycho_data, colWidths=[2*inch, 1*inch, 2*inch])
        else:
            assess_table = Table(affect_data, colWidths=[2*inch, 1*inch, 2*inch])

        assess_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(assess_table)
        elements.append(Spacer(1, 0.2*inch))

    # ============================================================
    # ATTENDANCE
    # ============================================================
    if attendance:
        elements.append(Paragraph("<b>ATTENDANCE RECORD</b>", 
                                ParagraphStyle('SectionHeader2', parent=title_style, 
                                              textColor=colors.HexColor('#1a5276'), 
                                              fontSize=11, spaceAfter=6)))
        
        att_data = [
            ['School Days Opened', 'Times Present', 'Times Absent', 'Times Late'],
            [str(attendance.school_opened or 0), 
             str(attendance.times_present or 0),
             str(attendance.times_absent or 0),
             str(attendance.times_late or 0)]
        ]
        
        att_table = Table(att_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        att_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(att_table)
        elements.append(Spacer(1, 0.2*inch))

    # ============================================================
    # COMMENTS
    # ============================================================
    if comments:
        elements.append(Paragraph("<b>REMARKS & COMMENTS</b>", 
                                ParagraphStyle('SectionHeader3', parent=title_style, 
                                              textColor=colors.HexColor('#1a5276'), 
                                              fontSize=11, spaceAfter=6)))
        
        comment_data = []
        if comments.class_teacher_comment:
            comment_data.append([
                Paragraph('<b>Class Teacher\'s Comment:</b>', title_style),
                Paragraph(comments.class_teacher_comment, normal_style)
            ])
        if comments.principal_comment:
            comment_data.append([
                Paragraph('<b>Principal\'s Comment:</b>', title_style),
                Paragraph(comments.principal_comment, normal_style)
            ])
        if comments.achievement_box:
            comment_data.append([
                Paragraph('<b>Special Achievement:</b>', title_style),
                Paragraph(comments.achievement_box, normal_style)
            ])
        
        if comment_data:
            comment_table = Table(comment_data, colWidths=[1.8*inch, 4.2*inch])
            comment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#eaf2f8')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(comment_table)
            elements.append(Spacer(1, 0.2*inch))

    # ============================================================
    # GRADE LEGEND
    # ============================================================
    elements.append(Paragraph("<b>GRADE LEGEND</b>", 
                            ParagraphStyle('SectionHeader4', parent=title_style, 
                                          textColor=colors.HexColor('#1a5276'), 
                                          fontSize=11, spaceAfter=6)))
    
    legend_data = [['Grade', 'Score Range', 'Point', 'Remark']]
    for grade_code, details in GRADING_SYSTEM.items():
        legend_data.append([
            grade_code,
            f"{details['min']}-{details['max']}",
            str(details['point']),
            details['remark']
        ])
    
    legend_table = Table(legend_data, colWidths=[1*inch, 1.5*inch, 1*inch, 2.5*inch])
    legend_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5276')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(legend_table)

    # ============================================================
    # FOOTER / SIGNATURES
    # ============================================================
    elements.append(Spacer(1, 0.3*inch))
    sig_data = [
        ['_______________________', '_______________________', '_______________________'],
        ['Class Teacher', 'Principal', 'Date'],
    ]
    sig_table = Table(sig_data, colWidths=[2*inch, 2*inch, 2*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(sig_table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"report_card_{student.admission_number}.pdf",
        mimetype='application/pdf'
    )

# ============================================================
# ROUTES - SUBJECT ALLOCATION
# ============================================================

@app.route('/subjects')
@login_required
def subjects_list():
    subjects = Subject.query.filter_by(is_active=True).all()
    return render_template('subjects/list.html', subjects=subjects)

@app.route('/subjects/allocate', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal'])
def subject_allocate():
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        subject_id = request.form.get('subject_id')
        teacher_id = request.form.get('teacher_id')
        session_id = request.form.get('session_id')
        is_compulsory = request.form.get('is_compulsory') == 'on'

        allocation = ClassSubject(
            class_id=class_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            session_id=session_id,
            is_compulsory=is_compulsory
        )
        db.session.add(allocation)
        db.session.commit()

        flash('Subject allocated successfully!', 'success')
        return redirect(url_for('subjects_list'))

    classes = Class.query.filter_by(is_active=True).all()
    subjects = Subject.query.filter_by(is_active=True).all()
    teachers = Staff.query.filter_by(is_active=True).all()
    sessions = Session.query.all()

    return render_template('subjects/allocate.html',
                         classes=classes, subjects=subjects,
                         teachers=teachers, sessions=sessions)

@app.route('/subjects/student-enroll', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal', 'teacher'])
def student_subject_enroll():
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        subject_ids = request.form.getlist('subject_ids')
        session_id = request.form.get('session_id')

        student = Student.query.get(student_id)

        for subject_id in subject_ids:
            enrollment = StudentSubject(
                student_id=student_id,
                subject_id=subject_id,
                class_id=student.class_id,
                session_id=session_id
            )
            db.session.add(enrollment)

        db.session.commit()
        flash('Subjects enrolled successfully!', 'success')
        return redirect(url_for('student_subject_enroll'))

    students = Student.query.filter_by(status='active').all()
    sessions = Session.query.all()

    return render_template('subjects/student_enroll.html',
                         students=students, sessions=sessions)

# ============================================================
# ROUTES - FEE MANAGEMENT
# ============================================================

@app.route('/fees')
@login_required
@role_required(['admin', 'bursar'])
def fees_list():
    fees = SchoolFee.query.order_by(SchoolFee.created_at.desc()).all()
    return render_template('fees/list.html', fees=fees)

@app.route('/fees/setup', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'bursar'])
def fee_setup():
    if request.method == 'POST':
        fee = SchoolFee(
            class_id=request.form.get('class_id'),
            department_id=request.form.get('department_id'),
            session_id=request.form.get('session_id'),
            term_id=request.form.get('term_id'),
            fee_type=request.form.get('fee_type'),
            amount=request.form.get('amount'),
            description=request.form.get('description'),
            due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date() if request.form.get('due_date') else None,
            is_mandatory=request.form.get('is_mandatory') == 'on',
            created_by=current_user.id
        )
        db.session.add(fee)
        db.session.commit()

        flash('Fee setup successfully!', 'success')
        return redirect(url_for('fees_list'))

    classes = Class.query.filter_by(is_active=True).all()
    departments = Department.query.all()
    sessions = Session.query.all()
    terms = Term.query.all()

    return render_template('fees/setup.html',
                         classes=classes, departments=departments,
                         sessions=sessions, terms=terms)

@app.route('/fees/payment', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'bursar'])
def fee_payment():
    if request.method == 'POST':
        payment = FeePayment(
            student_id=request.form.get('student_id'),
            fee_id=request.form.get('fee_id'),
            amount_paid=request.form.get('amount_paid'),
            amount_due=request.form.get('amount_due'),
            payment_method=request.form.get('payment_method'),
            transaction_reference=request.form.get('transaction_reference'),
            received_by=current_user.id,
            remarks=request.form.get('remarks')
        )
        db.session.add(payment)
        db.session.commit()

        flash('Payment recorded successfully!', 'success')
        return redirect(url_for('fees_list'))

    students = Student.query.filter_by(status='active').all()
    fees = SchoolFee.query.all()

    return render_template('fees/payment.html', students=students, fees=fees)

@app.route('/api/student-fees/<int:student_id>')
@login_required
def student_fees_api(student_id):
    """API to get student fee details"""
    payments = FeePayment.query.filter_by(student_id=student_id).all()

    total_paid = sum(float(p.amount_paid) for p in payments)
    total_due = sum(float(p.amount_due) for p in payments) if payments else 0
    balance = total_due - total_paid

    return jsonify({
        'total_paid': total_paid,
        'total_due': total_due,
        'balance': balance,
        'payments': [{
            'date': p.payment_date.isoformat(),
            'amount': float(p.amount_paid),
            'method': p.payment_method,
            'reference': p.transaction_reference
        } for p in payments]
    })

# ============================================================
# ROUTES - ATTENDANCE
# ============================================================

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal', 'teacher'])
def attendance_manage():
    if request.method == 'POST':
        class_id = request.form.get('class_id')
        session_id = request.form.get('session_id')
        term_id = request.form.get('term_id')

        students = Student.query.filter_by(class_id=class_id, status='active').all()

        for student in students:
            att = Attendance.query.filter_by(
                student_id=student.id,
                session_id=session_id,
                term_id=term_id
            ).first()

            if not att:
                att = Attendance(
                    student_id=student.id,
                    class_id=class_id,
                    session_id=session_id,
                    term_id=term_id
                )
                db.session.add(att)

            att.school_opened = int(request.form.get(f'school_opened_{student.id}', 0))
            att.times_present = int(request.form.get(f'present_{student.id}', 0))
            att.times_absent = int(request.form.get(f'absent_{student.id}', 0))
            att.times_late = int(request.form.get(f'late_{student.id}', 0))
            att.updated_by = current_user.id

        db.session.commit()
        flash('Attendance updated successfully!', 'success')
        return redirect(url_for('attendance_manage'))

    classes = Class.query.filter_by(is_active=True).all()
    sessions = Session.query.all()
    terms = Term.query.all()

    class_id = request.args.get('class_id')
    session_id = request.args.get('session_id')
    term_id = request.args.get('term_id')

    students = []
    if class_id:
        students = Student.query.filter_by(class_id=class_id, status='active').all()

    return render_template('attendance/manage.html',
                         classes=classes, sessions=sessions, terms=terms,
                         students=students, class_id=class_id,
                         session_id=session_id, term_id=term_id)

# ============================================================
# ROUTES - SETTINGS & ADMINISTRATION
# ============================================================

@app.route('/settings', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def settings():
    setting = Setting.query.first()
    if not setting:
        setting = Setting()
        db.session.add(setting)
        db.session.commit()

    if request.method == 'POST':
        setting.school_name = request.form.get('school_name')
        setting.school_address = request.form.get('school_address')
        setting.school_phone = request.form.get('school_phone')
        setting.school_email = request.form.get('school_email')
        setting.school_motto = request.form.get('school_motto')
        setting.current_session = request.form.get('current_session')
        setting.current_term = request.form.get('current_term')
        setting.ca_max_score = request.form.get('ca_max_score', 30)
        setting.exam_max_score = request.form.get('exam_max_score', 70)

        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('settings'))

    sessions = Session.query.all()
    terms = Term.query.all()

    return render_template('settings.html', setting=setting, sessions=sessions, terms=terms)

@app.route('/users')
@login_required
@role_required(['admin'])
def users_list():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@app.route('/users/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin'])
def user_create():
    if request.method == 'POST':
        user = User(
            username=request.form.get('username'),
            password_hash=generate_password_hash(request.form.get('password')),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            role=request.form.get('role')
        )
        db.session.add(user)
        db.session.commit()

        flash('User created successfully!', 'success')
        return redirect(url_for('users_list'))

    return render_template('users/create.html')

    # ============================================================
# ROUTES - SESSION MANAGEMENT
# ============================================================

@app.route('/sessions')
@login_required
@role_required(['admin', 'principal'])
def sessions_list():
    sessions = Session.query.order_by(Session.name.desc()).all()
    return render_template('sessions/list.html', sessions=sessions)

@app.route('/sessions/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal'])
def session_create():
    if request.method == 'POST':
        session_obj = Session(
            name=request.form.get('name'),
            start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date() if request.form.get('start_date') else None,
            end_date=datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date() if request.form.get('end_date') else None,
            is_active=request.form.get('is_active') == 'on'
        )
        
        # If setting this as active, deactivate others
        if session_obj.is_active:
            Session.query.update({Session.is_active: False})
        
        db.session.add(session_obj)
        db.session.commit()
        
        flash(f'Session "{session_obj.name}" created successfully!', 'success')
        return redirect(url_for('sessions_list'))
    
    return render_template('sessions/create.html')

@app.route('/sessions/<int:session_id>/activate', methods=['POST'])
@login_required
@role_required(['admin', 'principal'])
def session_activate(session_id):
    # Deactivate all sessions
    Session.query.update({Session.is_active: False})
    
    # Activate selected session
    session_obj = Session.query.get_or_404(session_id)
    session_obj.is_active = True
    db.session.commit()
    
    flash(f'Session "{session_obj.name}" is now active!', 'success')
    return redirect(url_for('sessions_list'))

# ============================================================
# ROUTES - STAFF MANAGEMENT
# ============================================================

@app.route('/staff')
@login_required
@role_required(['admin', 'principal'])
def staff_list():
    staff = Staff.query.order_by(Staff.created_at.desc()).all()
    return render_template('staff/list.html', staff=staff)

@app.route('/staff/register', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'principal'])
def staff_register():
    if request.method == 'POST':
        staff = Staff(
            staff_id=request.form.get('staff_id'),
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            other_names=request.form.get('other_names'),
            sex=request.form.get('sex'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date() if request.form.get('date_of_birth') else None,
            qualification=request.form.get('qualification'),
            department_id=request.form.get('department_id'),
            designation=request.form.get('designation'),
            phone=request.form.get('phone'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            date_employed=datetime.strptime(request.form.get('date_employed'), '%Y-%m-%d').date() if request.form.get('date_employed') else None
        )
        
        db.session.add(staff)
        db.session.commit()
        
        flash(f'Staff "{staff.first_name} {staff.last_name}" registered successfully!', 'success')
        return redirect(url_for('staff_list'))
    
    departments = Department.query.all()
    return render_template('staff/register.html', departments=departments)



# ============================================================
# API ENDPOINTS
# ============================================================

@app.route('/api/students')
@login_required
def api_students():
    """API endpoint to get students"""
    class_id = request.args.get('class_id')
    query = Student.query.filter_by(status='active')
    if class_id:
        query = query.filter_by(class_id=class_id)
    students = query.all()

    return jsonify([{
        'id': s.id,
        'admission_number': s.admission_number,
        'name': f"{s.first_name} {s.last_name}",
        'class': s.student_class.name if s.student_class else None,
        'sex': s.sex
    } for s in students])

@app.route('/api/subjects/<int:class_id>')
@login_required
def api_class_subjects(class_id):
    """API endpoint to get subjects for a class"""
    class_subjects = ClassSubject.query.filter_by(class_id=class_id).all()
    return jsonify([{
        'id': cs.subject.id,
        'name': cs.subject.name,
        'code': cs.subject.code,
        'is_compulsory': cs.is_compulsory
    } for cs in class_subjects])

@app.route('/api/results/summary')
@login_required
def api_results_summary():
    """API endpoint for results summary dashboard"""
    session_id = request.args.get('session_id')
    term_id = request.args.get('term_id')

    total_results = TermResult.query.filter_by(
        session_id=session_id, term_id=term_id
    ).count()

    avg_score = db.session.query(db.func.avg(TermResult.total_score)).filter_by(
        session_id=session_id, term_id=term_id
    ).scalar() or 0

    pass_count = TermResult.query.filter(
        TermResult.session_id == session_id,
        TermResult.term_id == term_id,
        TermResult.total_score >= 40
    ).count()

    return jsonify({
        'total_results': total_results,
        'average_score': round(float(avg_score), 2),
        'pass_count': pass_count,
        'pass_rate': round((pass_count / total_results * 100), 2) if total_results > 0 else 0
    })

@app.template_filter('ordinal')
def ordinal_filter(n):
    if n is None:
        return 'N/A'
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"
# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ============================================================
# INITIALIZATION
# ============================================================

def init_db():
    with app.app_context():
        db.create_all()

        # Create default admin if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@gfaschool.edu.ng',
                role='admin'
            )
            db.session.add(admin)

        # Create default terms
        if not Term.query.first():
            terms = [
                Term(name='First Term', term_number=1, description='First Academic Term'),
                Term(name='Second Term', term_number=2, description='Second Academic Term'),
                Term(name='Third Term', term_number=3, description='Third Academic Term')
            ]
            db.session.add_all(terms)

        # Create default departments
        if not Department.query.first():
            depts = [
                Department(name='JSS (Junior Secondary)', code='JSS', description='Junior Secondary School'),
                Department(name='Science', code='SCI', description='Science Department'),
                Department(name='Commercial', code='COM', description='Commercial Department'),
                Department(name='Arts', code='ART', description='Arts Department')
            ]
            db.session.add_all(depts)

        # Create default classes
        if not Class.query.first():
            classes = [
                Class(name='JSS 1', level='JSS', capacity=40),
                Class(name='JSS 2', level='JSS', capacity=40),
                Class(name='JSS 3', level='JSS', capacity=40),
                Class(name='SSS 1', level='SSS', capacity=40),
                Class(name='SSS 2', level='SSS', capacity=40),
                Class(name='SSS 3', level='SSS', capacity=40)
            ]
            db.session.add_all(classes)

        # Create default subjects
        if not Subject.query.first():
            subjects = [
                Subject(name='Religious and Moral Instructions', code='RMI', category='Core'),
                Subject(name='Computer Study', code='CMP', category='Core'),
                Subject(name='Business Study', code='BUS', category='Elective'),
                Subject(name='Cultural and Creative Arts/Music', code='CCA', category='Elective'),
                Subject(name='Basic Technology', code='BAS', category='Core'),
                Subject(name='Civic Education', code='CIV', category='Core'),
                Subject(name='Yoruba Language', code='YOR', category='Core'),
                Subject(name='English Language', code='ENG', category='Core'),
                Subject(name='Mathematics', code='MAT', category='Core'),
                Subject(name='Basic Science', code='BSC', category='Core'),
                Subject(name='Prevocational Studies', code='PVS', category='Elective'),
                Subject(name='National Values Education', code='NVE', category='Core'),
                Subject(name='Physical Education', code='PED', category='Core'),
                Subject(name='French', code='FRE', category='Elective'),
                Subject(name='Christian Religious Knowledge', code='CRK', category='Core'),
                Subject(name='Physics', code='PHY', category='Core'),
                Subject(name='Chemistry', code='CHM', category='Core'),
                Subject(name='Biology', code='BIO', category='Core'),
                Subject(name='Animal Husbandry', code='AHB', category='Elective'),
                Subject(name='Data Processing', code='DAP', category='Elective'),
                Subject(name='Agricultural Science', code='AGR', category='Elective'),
                Subject(name='Further Mathematics', code='FMA', category='Elective'),
                Subject(name='Financial Accounting', code='FAC', category='Core'),
                Subject(name='Commerce', code='COM', category='Core'),
                Subject(name='Economics', code='ECO', category='Core'),
                Subject(name='Geography', code='GEO', category='Elective'),
                Subject(name='Government', code='GOV', category='Core'),
                Subject(name='Literature-in-English', code='LIT', category='Core')
            ]
            db.session.add_all(subjects)

        # Create default settings
        if not Setting.query.first():
            setting = Setting(
                school_name='Secondary School',
                current_session='2025/2026',
                current_term=1,
                ca_max_score=30,
                exam_max_score=70
            )
            db.session.add(setting)

        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
