# GFA SCHOOL MANAGEMENT SYSTEM
## Complete Design & Implementation Document
### For JSS and SSS (Junior & Senior Secondary School)

---

## TABLE OF CONTENTS

1. [System Overview](#1-system-overview)
2. [Requirements Analysis](#2-requirements-analysis)
3. [System Architecture](#3-system-architecture)
4. [Database Design](#4-database-design)
5. [Module Design](#5-module-design)
6. [User Interface Design](#6-user-interface-design)
7. [Implementation Details](#7-implementation-details)
8. [Security Features](#8-security-features)
9. [Deployment Guide](#9-deployment-guide)
10. [Appendices](#10-appendices)

---

## 1. SYSTEM OVERVIEW

### 1.1 Introduction
The GFA School Management System is a comprehensive web-based application designed to automate and streamline the administrative and academic operations of GFA Secondary School, covering both Junior Secondary School (JSS) and Senior Secondary School (SSS).

### 1.2 Objectives
- Automate student registration and record management
- Process academic results per term and session
- Manage subject allocation across departments
- Track school fees and payments
- Generate comprehensive report cards
- Provide role-based access for different user types

### 1.3 Scope
**In Scope:**
- Student registration and profile management
- Multi-term result processing (First, Second, Third Term)
- Session-wide result aggregation
- Subject allocation per class/department
- Grade calculation with Nigerian grading system
- Psychomotor and affective assessment
- Attendance tracking
- School fees management
- Report card generation (Print & PDF)
- Role-based access control

**Out of Scope:**
- Online learning management
- Parent portal (Phase 2)
- SMS/Email notifications (Phase 2)
- Biometric attendance (Phase 2)

---

## 2. REQUIREMENTS ANALYSIS

### 2.1 Functional Requirements

#### 2.1.1 Student Management (FR-SM)
| ID | Requirement | Priority |
|---|---|---|
| FR-SM-01 | Register new students with auto-generated admission numbers | High |
| FR-SM-02 | Store personal, contact, and academic information | High |
| FR-SM-03 | Track student status (Active, Suspended, Withdrawn, Graduated) | High |
| FR-SM-04 | Manage parent/guardian information | High |
| FR-SM-05 | Search and filter students by class, status | Medium |
| FR-SM-06 | Generate student ID cards | Low |

#### 2.1.2 Result Processing (FR-RP)
| ID | Requirement | Priority |
|---|---|---|
| FR-RP-01 | Enter C.A scores (max 30) and Exam scores (max 70) | High |
| FR-RP-02 | Automatic calculation of total, grade, and remark | High |
| FR-RP-03 | Calculate subject positions within class | High |
| FR-RP-04 | Aggregate results across three terms per session | High |
| FR-RP-05 | Calculate class and year positions | Medium |
| FR-RP-06 | Handle result verification workflow | Medium |

#### 2.1.3 Subject Allocation (FR-SA)
| ID | Requirement | Priority |
|---|---|---|
| FR-SA-01 | Define subjects per class and department | High |
| FR-SA-02 | Assign subject teachers | High |
| FR-SA-03 | Enroll students in elective subjects (SSS) | High |
| FR-SA-04 | Manage compulsory vs elective subjects | Medium |

#### 2.1.4 Fee Management (FR-FM)
| ID | Requirement | Priority |
|---|---|---|
| FR-FM-01 | Setup fee structures per class/session/term | High |
| FR-FM-02 | Record fee payments with multiple methods | High |
| FR-FM-03 | Calculate and track balances | High |
| FR-FM-04 | Generate fee receipts | Medium |
| FR-FM-05 | Fee reports and analytics | Low |

#### 2.1.5 Report Generation (FR-RG)
| ID | Requirement | Priority |
|---|---|---|
| FR-RG-01 | Generate comprehensive report cards per term | High |
| FR-RG-02 | Include psychomotor and affective assessments | High |
| FR-RG-03 | Include class teacher and principal comments | High |
| FR-RG-04 | Print and PDF download options | High |
| FR-RG-05 | Session-wide cumulative reports | Medium |

### 2.2 Non-Functional Requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-01 | System response time | < 2 seconds |
| NFR-02 | Concurrent users | 50+ |
| NFR-03 | Data backup | Daily automated |
| NFR-04 | Uptime | 99.5% |
| NFR-05 | Browser compatibility | Chrome, Firefox, Edge, Safari |
| NFR-06 | Mobile responsiveness | Responsive design |

---

## 3. SYSTEM ARCHITECTURE

### 3.1 Architecture Pattern
**Model-View-Controller (MVC) with 3-Tier Architecture**

```
┌─────────────────────────────────────────┐
│           PRESENTATION LAYER            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │  HTML   │ │  CSS    │ │JavaScript│  │
│  │Templates│ │Bootstrap│ │  jQuery  │  │
│  └─────────┘ └─────────┘ └─────────┘  │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│           APPLICATION LAYER             │
│  ┌─────────────────────────────────┐    │
│  │         Flask Framework          │    │
│  │  ┌─────────┐    ┌────────────┐ │    │
│  │  │  Views  │◄──►│  Controllers│ │    │
│  │  │ (Routes)│    │  (Logic)   │ │    │
│  │  └─────────┘    └────────────┘ │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│            DATA LAYER                   │
│  ┌─────────────┐    ┌──────────────┐   │
│  │  SQLAlchemy │◄──►│  PostgreSQL  │   │
│  │    ORM      │    │   Database   │   │
│  └─────────────┘    └──────────────┘   │
└─────────────────────────────────────────┘
```

### 3.2 Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Backend | Python | 3.8+ | Programming language |
| Framework | Flask | 2.3.3 | Web framework |
| ORM | SQLAlchemy | 3.0.5 | Database ORM |
| Database | PostgreSQL | 12+ | Relational database |
| Authentication | Flask-Login | 0.6.2 | Session management |
| Security | Werkzeug | 2.3.7 | Password hashing |
| Frontend | Bootstrap | 5.3.0 | CSS framework |
| Icons | Font Awesome | 6.4.0 | Icon library |
| PDF | ReportLab | 4.0.4 | PDF generation |
| JS Library | jQuery | 3.6.0 | DOM manipulation |

### 3.3 System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    GFA SCHOOL MANAGEMENT SYSTEM               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Student   │  │   Result    │  │   Subject   │         │
│  │   Module    │  │   Module    │  │   Module    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Fee      │  │   Report    │  │   Admin     │         │
│  │   Module    │  │   Module    │  │   Module    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  ┌─────────────┐  ┌─────────────┐                          │
│  │ Attendance  │  │ Assessment  │                          │
│  │   Module    │  │   Module    │                          │
│  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. DATABASE DESIGN

### 4.1 Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   users     │       │   staff     │       │ departments │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──────┤ user_id(FK) │       │ id (PK)     │
│ username    │       │ staff_id    │◄──────┤ head_of_dept│
│ password    │       │ first_name  │       │ name        │
│ role        │       │ department  │──────►│ code        │
└─────────────┘       └─────────────┘       └─────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │   classes   │
                       ├─────────────┤
                       │ id (PK)     │
                       │ name        │
                       │ level       │
                       │ class_teacher│◄──── staff.id
                       └─────────────┘
                              │
                              ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   students  │       │   subjects  │       │  sessions   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ admission_no│       │ name        │       │ name        │
│ class_id(FK)│◄──────┤ code        │       │ is_active   │
│ user_id(FK) │       │ category    │       └─────────────┘
└─────────────┘       └─────────────┘              │
      │                    │                     │
      └────────────────────┼─────────────────────┘
                           ▼
              ┌─────────────────────┐
              │    term_results     │
              ├─────────────────────┤
              │ id (PK)             │
              │ student_id (FK)     │
              │ subject_id (FK)     │
              │ class_id (FK)       │
              │ session_id (FK)     │
              │ term_id (FK)        │
              │ ca_score (0-30)     │
              │ exam_score (0-70)   │
              │ total_score         │
              │ grade               │
              │ grade_point         │
              │ subject_position    │
              └─────────────────────┘
                           │
                           ▼
              ┌─────────────────────┐
              │   session_results   │
              ├─────────────────────┤
              │ id (PK)             │
              │ student_id (FK)     │
              │ first_term_total      │
              │ second_term_total     │
              │ third_term_total      │
              │ sessional_avg         │
              │ sessional_grade       │
              │ sessional_position    │
              │ promotion_status      │
              └─────────────────────┘
```

### 4.2 Table Specifications

#### 4.2.1 Core Tables

**users**
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| username | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| password_hash | VARCHAR(255) | NOT NULL | Hashed password |
| email | VARCHAR(100) | UNIQUE | Email address |
| phone | VARCHAR(20) | | Phone number |
| role | VARCHAR(20) | CHECK | User role |
| is_active | BOOLEAN | DEFAULT TRUE | Account status |
| last_login | TIMESTAMP | | Last login time |
| created_at | TIMESTAMP | DEFAULT NOW() | Creation timestamp |

**students**
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| admission_number | VARCHAR(20) | UNIQUE, NOT NULL | Auto-generated |
| first_name | VARCHAR(50) | NOT NULL | First name |
| last_name | VARCHAR(50) | NOT NULL | Last name |
| other_names | VARCHAR(50) | | Other names |
| sex | VARCHAR(10) | CHECK | Male/Female |
| date_of_birth | DATE | | Date of birth |
| class_id | INTEGER | FK → classes | Current class |
| department_id | INTEGER | FK → departments | SSS department |
| status | VARCHAR(20) | DEFAULT 'active' | Student status |

#### 4.2.2 Academic Tables

**term_results**
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| student_id | INTEGER | FK, NOT NULL | Student reference |
| subject_id | INTEGER | FK, NOT NULL | Subject reference |
| ca_score | INTEGER | CHECK (0-30) | Continuous Assessment |
| exam_score | INTEGER | CHECK (0-70) | Examination score |
| total_score | INTEGER | GENERATED | CA + Exam |
| grade | VARCHAR(5) | | Calculated grade |
| grade_point | DECIMAL(3,2) | | Grade point |
| remark | VARCHAR(20) | | Performance remark |
| subject_position | INTEGER | | Rank in subject |

**Grading System (Nigerian Standard)**
| Grade | Range | Point | Remark |
|---|---|---|---|
| A1 | 75-100 | 5.0 | Excellent |
| B2 | 70-74 | 4.5 | Very Good |
| B3 | 65-69 | 4.0 | Good |
| C4 | 60-64 | 3.75 | Credit |
| C5 | 55-59 | 3.25 | Credit |
| C6 | 50-54 | 3.0 | Credit |
| D7 | 45-49 | 2.0 | Pass |
| E8 | 40-44 | 1.0 | Pass |
| F9 | 0-39 | 0.0 | Fail |

#### 4.2.3 Assessment Tables

**psychomotor_assessments**
| Column | Type | Constraints | Description |
|---|---|---|---|
| id | SERIAL | PRIMARY KEY | Unique identifier |
| student_id | INTEGER | FK | Student reference |
| handwriting | INTEGER | CHECK (1-5) | Handwriting skill |
| verbal_fluency | INTEGER | CHECK (1-5) | Speaking ability |
| sports | INTEGER | CHECK (1-5) | Sports ability |
| handling_tools | INTEGER | CHECK (1-5) | Tool handling |
| drawing_painting | INTEGER | CHECK (1-5) | Art skills |
| musical_skills | INTEGER | CHECK (1-5) | Music ability |

**Rating Scale:**
- 5 = Excellent
- 4 = Good
- 3 = Fair
- 2 = Poor
- 1 = Very Poor

### 4.3 Indexes

```sql
CREATE INDEX idx_students_class ON students(class_id);
CREATE INDEX idx_students_admission ON students(admission_number);
CREATE INDEX idx_term_results_student ON term_results(student_id);
CREATE INDEX idx_term_results_session ON term_results(session_id, term_id);
CREATE INDEX idx_attendance_student ON attendance(student_id, session_id, term_id);
CREATE INDEX idx_fee_payments_student ON fee_payments(student_id);
```

---

## 5. MODULE DESIGN

### 5.1 Student Management Module

**Classes:**
- `Student` (Model)
- `StudentRegistrationForm` (View)
- `StudentProfileView` (View)
- `StudentListView` (View)

**Key Methods:**
```python
def register_student(data):
    """Register new student with auto-generated admission number"""
    admission_number = generate_admission_number()
    student = Student(**data, admission_number=admission_number)
    db.session.add(student)
    db.session.commit()
    return student

def generate_admission_number():
    """Generate format: GFA/YYYY/XXXX"""
    year = datetime.now().year
    count = Student.query.filter(
        extract('year', Student.created_at) == year
    ).count() + 1
    return f"GFA/{year}/{count:04d}"
```

### 5.2 Result Processing Module

**Classes:**
- `TermResult` (Model)
- `SessionResult` (Model)
- `ResultEntryForm` (View)
- `GradeCalculator` (Utility)

**Key Methods:**
```python
def calculate_grade(total_score):
    """Calculate grade based on Nigerian grading system"""
    grading_system = {
        'A1': (75, 100, 5.0, 'Excellent'),
        'B2': (70, 74, 4.5, 'Very Good'),
        'B3': (65, 69, 4.0, 'Good'),
        'C4': (60, 64, 3.75, 'Credit'),
        'C5': (55, 59, 3.25, 'Credit'),
        'C6': (50, 54, 3.0, 'Credit'),
        'D7': (45, 49, 2.0, 'Pass'),
        'E8': (40, 44, 1.0, 'Pass'),
        'F9': (0, 39, 0.0, 'Fail')
    }
    for grade, (min_score, max_score, point, remark) in grading_system.items():
        if min_score <= total_score <= max_score:
            return grade, point, remark
    return 'F9', 0.0, 'Fail'

def calculate_positions(class_id, subject_id, session_id, term_id):
    """Calculate subject positions for all students in a class"""
    results = TermResult.query.filter_by(
        class_id=class_id,
        subject_id=subject_id,
        session_id=session_id,
        term_id=term_id
    ).order_by(TermResult.total_score.desc()).all()

    for position, result in enumerate(results, 1):
        result.subject_position = position
    db.session.commit()
```

### 5.3 Subject Allocation Module

**JSS Subjects (15 total):**
1. Religious and Moral Instructions
2. Computer Study
3. Business Study
4. Cultural and Creative Arts/Music
5. Basic Technology
6. Civic Education
7. Yoruba Language
8. English Language
9. Mathematics
10. Basic Science
11. Prevocational Studies
12. National Values Education
13. Physical Education
14. French
15. Christian Religious Knowledge

**SSS Science (14 subjects):**
1. Physics
2. Chemistry
3. Biology
4. Mathematics
5. English Language
6. Animal Husbandry
7. Data Processing
8. Yoruba Language
9. Agricultural Science
10. Civic Education
11. Geography
12. Economics
13. Further Mathematics
14. Religious and Moral Instructions

**SSS Commercial (13 subjects):**
1. Financial Accounting
2. Commerce
3. Economics
4. Geography
5. Government
6. Agricultural Science
7. Biology
8. Yoruba Language
9. English Language
10. Mathematics
11. Further Mathematics
12. Religious and Moral Instructions
13. Civic Education

**SSS Arts (14 subjects):**
1. Literature-in-English
2. Christian Religious Knowledge
3. Government
4. Biology
5. French
6. Economics
7. Religious and Moral Instructions
8. Mathematics
9. English Language
10. Further Mathematics
11. Civic Education
12. Data Processing
13. Animal Husbandry
14. Yoruba Language

### 5.4 Fee Management Module

**Fee Types:**
- Tuition Fee
- Examination Fee
- Sports Fee
- Library Fee
- Development Levy
- PTA Levy
- Medical Fee
- Others

**Payment Methods:**
- Cash
- Bank Transfer
- POS
- Online Payment
- Cheque

### 5.5 Report Generation Module

**Report Card Components:**
1. School Header (Name, Logo, Motto)
2. Student Information
3. Attendance Summary
4. Academic Results Table
5. Grade Legend
6. Psychomotor Skills Assessment
7. Affective Disposition Assessment
8. Achievement Box
9. Class Teacher Comment
10. Principal Comment
11. Signatures and Dates

---

## 6. USER INTERFACE DESIGN

### 6.1 Navigation Structure

```
Dashboard
├── Students
│   ├── List Students
│   ├── Register Student
│   └── Student Profile
├── Academics
│   ├── Result Entry
│   ├── View Results
│   ├── Psychomotor Assessment
│   ├── Affective Assessment
│   └── Attendance
├── Subjects
│   ├── List Subjects
│   ├── Allocate Subjects
│   └── Student Enrollment
├── Finance
│   ├── Fee Setup
│   ├── Record Payment
│   └── Fee Reports
├── Reports
│   └── Report Cards
└── Administration (Admin Only)
    ├── Users
    ├── Settings
    └── System Logs
```

### 6.2 Role-Based Views

**Admin:**
- Full access to all modules
- User management
- System configuration
- Data backup/restore

**Principal:**
- View all results
- Approve result comments
- Generate reports
- View analytics

**Teacher:**
- Enter results for assigned subjects
- Manage attendance
- Conduct assessments
- Add comments

**Bursar:**
- Fee setup and management
- Payment recording
- Financial reports
- Balance tracking

**Student/Parent:**
- View-only access to own records
- View report cards
- Check fee balance

---

## 7. IMPLEMENTATION DETAILS

### 7.1 Project Structure

```
school_management_system/
├── app.py                  # Main application file
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── database.sql            # Database schema
├── README.md               # Documentation
├── templates/
│   ├── base.html           # Base layout
│   ├── login.html          # Login page
│   ├── dashboard.html      # Dashboard
│   ├── settings.html       # System settings
│   ├── students/
│   │   ├── list.html       # Student list
│   │   ├── register.html   # Registration form
│   │   ├── profile.html    # Student profile
│   │   └── edit.html       # Edit student
│   ├── results/
│   │   ├── entry.html      # Result entry
│   │   └── view.html       # View results
│   ├── reports/
│   │   └── report_card.html # Report card
│   ├── fees/
│   │   ├── list.html       # Fee list
│   │   ├── setup.html      # Fee setup
│   │   └── payment.html    # Payment entry
│   ├── attendance/
│   │   └── manage.html     # Attendance
│   ├── assessments/
│   │   ├── psychomotor.html # Psychomotor
│   │   └── affective.html   # Affective
│   └── errors/
│       ├── 404.html        # Not found
│       └── 500.html        # Server error
└── static/
    ├── css/                # Custom styles
    ├── js/                 # Custom scripts
    └── uploads/            # File uploads
```

### 7.2 Key Implementation Features

**1. Auto-generated Admission Numbers:**
```python
def generate_admission_number():
    year = datetime.now().year
    count = Student.query.filter(
        extract('year', Student.created_at) == year
    ).count() + 1
    return f"GFA/{year}/{count:04d}"
# Example: GFA/2026/0001
```

**2. Automatic Grade Calculation:**
```python
def calculate_grade(total_score):
    if total_score >= 75: return 'A1', 5.0, 'Excellent'
    elif total_score >= 70: return 'B2', 4.5, 'Very Good'
    elif total_score >= 65: return 'B3', 4.0, 'Good'
    elif total_score >= 60: return 'C4', 3.75, 'Credit'
    elif total_score >= 55: return 'C5', 3.25, 'Credit'
    elif total_score >= 50: return 'C6', 3.0, 'Credit'
    elif total_score >= 45: return 'D7', 2.0, 'Pass'
    elif total_score >= 40: return 'E8', 1.0, 'Pass'
    else: return 'F9', 0.0, 'Fail'
```

**3. Session Aggregation:**
```python
def aggregate_session_results(student_id, session_id):
    # Get all three term results
    terms = [1, 2, 3]
    term_totals = []

    for term_id in terms:
        results = TermResult.query.filter_by(
            student_id=student_id,
            session_id=session_id,
            term_id=term_id
        ).all()
        if results:
            total = sum(r.total_score for r in results)
            avg = total / len(results)
            term_totals.append((total, avg))

    # Calculate sessional aggregate
    if len(term_totals) == 3:
        sessional_total = sum(t[0] for t in term_totals)
        sessional_avg = sum(t[1] for t in term_totals) / 3
        return sessional_total, sessional_avg
```

**4. PDF Report Generation:**
```python
def generate_report_card_pdf(student_id, session_id, term_id):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Add header
    elements.append(Paragraph("GFA SECONDARY SCHOOL", header_style))
    elements.append(Paragraph("Student Report Card", styles['Heading2']))

    # Add student info
    student_data = [...]
    elements.append(Table(student_data))

    # Add results
    results_data = [...]
    elements.append(Table(results_data))

    doc.build(elements)
    return buffer
```

---

## 8. SECURITY FEATURES

### 8.1 Authentication & Authorization

**Password Security:**
- Werkzeug password hashing (PBKDF2 with SHA-256)
- Minimum password complexity requirements
- Password reset functionality

**Session Management:**
- Flask-Login for session handling
- Secure cookie settings
- Session timeout after inactivity

**Role-Based Access Control (RBAC):**
```python
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                flash('Access denied', 'danger')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/admin-only')
@role_required(['admin'])
def admin_page():
    return render_template('admin.html')
```

### 8.2 Data Protection

**Input Validation:**
- Server-side validation for all forms
- SQL injection prevention via ORM
- XSS protection through template escaping
- CSRF token protection

**Data Integrity:**
- Foreign key constraints
- Unique constraints on critical fields
- Transaction support for multi-step operations

---

## 9. DEPLOYMENT GUIDE

### 9.1 System Requirements

**Server Requirements:**
- OS: Ubuntu 20.04 LTS or higher
- RAM: 4GB minimum
- Storage: 50GB SSD
- Network: Stable internet connection

**Software Requirements:**
- Python 3.8+
- PostgreSQL 12+
- Nginx (reverse proxy)
- Gunicorn (WSGI server)
- SSL Certificate (Let's Encrypt)

### 9.2 Installation Steps

**Step 1: System Update**
```bash
sudo apt update && sudo apt upgrade -y
```

**Step 2: Install Dependencies**
```bash
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx
```

**Step 3: Database Setup**
```bash
sudo -u postgres createdb gfa_school_db
sudo -u postgres createuser -P gfa_admin
```

**Step 4: Application Setup**
```bash
cd /var/www/
git clone <repository-url> school_management
cd school_management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Step 5: Environment Configuration**
```bash
export SECRET_KEY='your-secure-secret-key'
export DATABASE_URL='postgresql://gfa_admin:password@localhost/gfa_school_db'
export FLASK_ENV='production'
```

**Step 6: Initialize Database**
```bash
python app.py
```

**Step 7: Gunicorn Configuration**
```bash
gunicorn -w 4 -b 127.0.0.1:8000 app:app
```

**Step 8: Nginx Configuration**
```nginx
server {
    listen 80;
    server_name school.gfa.edu.ng;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static/ {
        alias /var/www/school_management/static/;
    }
}
```

### 9.3 Backup Strategy

**Automated Daily Backups:**
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump gfa_school_db > /backup/db_backup_$DATE.sql
tar -czf /backup/files_backup_$DATE.tar.gz /var/www/school_management/static/uploads/
```

**Cron Job:**
```bash
0 2 * * * /var/www/school_management/backup.sh
```

---

## 10. APPENDICES

### Appendix A: Sample Report Card Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    GFA SECONDARY SCHOOL                     │
│                 Student Academic Report                    │
│              2025/2026 Session - First Term                │
├─────────────────────────────────────────────────────────────┤
│ Name: John Doe                    Admission No: GFA/2026/001│
│ Class: JSS 2                      Sex: Male                 │
├─────────────────────────────────────────────────────────────┤
│ SUBJECT          │ C.A │ EXAM │ TOTAL │ GRADE │ POSITION  │
├──────────────────┼─────┼──────┼───────┼───────┼───────────┤
│ English Language │ 25  │  65  │  90   │  A1   │    1st    │
│ Mathematics      │ 28  │  70  │  98   │  A1   │    1st    │
│ Basic Science    │ 22  │  60  │  82   │  B2   │    3rd    │
│ ...              │ ... │ ...  │  ...  │  ...  │    ...    │
├──────────────────┴─────┴──────┴───────┴───────┴───────────┤
│ Total Obtainable: 1500    Total Score: 1250                │
│ Student Average: 83.33%    Grade: B2 (Very Good)          │
├─────────────────────────────────────────────────────────────┤
│ PSYCHOMOTOR SKILLS                                         │
│ Handwriting: [4] Good    Sports: [5] Excellent             │
├─────────────────────────────────────────────────────────────┤
│ AFFECTIVE DISPOSITION                                      │
│ Punctuality: [5] Excellent  Attitude: [4] Good            │
├─────────────────────────────────────────────────────────────┤
│ Class Teacher's Comment:                                   │
│ Excellent performance. Keep up the good work.              │
│                                                            │
│ Principal's Comment:                                       │
│ A commendable result. Strive for excellence.             │
├─────────────────────────────────────────────────────────────┤
│                    Grade Legend                             │
│ A1: 75-100 (Excellent)  B2: 70-74 (Very Good)            │
│ B3: 65-69 (Good)        C4: 60-64 (Credit)               │
│ C5: 55-59 (Credit)      C6: 50-54 (Credit)              │
│ D7: 45-49 (Pass)        E8: 40-44 (Pass)                 │
│ F9: 0-39 (Fail)                                          │
└─────────────────────────────────────────────────────────────┘
```

### Appendix B: API Endpoints

| Endpoint | Method | Description | Auth Required |
|---|---|---|---|
| `/api/students` | GET | List students | Yes |
| `/api/students/<id>` | GET | Student details | Yes |
| `/api/results/summary` | GET | Results summary | Yes |
| `/api/student-fees/<id>` | GET | Fee details | Yes |
| `/api/subjects/<class_id>` | GET | Class subjects | Yes |

### Appendix C: Database Seed Data

**Default Admin Account:**
- Username: admin
- Password: admin123 (change on first login)
- Role: admin
- Email: admin@gfaschool.edu.ng

**Default Terms:**
1. First Term (Term 1)
2. Second Term (Term 2)
3. Third Term (Term 3)

**Default Departments:**
1. JSS (Junior Secondary)
2. Science
3. Commercial
4. Arts

**Default Classes:**
- JSS 1, JSS 2, JSS 3
- SSS 1, SSS 2, SSS 3

---

## DOCUMENT CONTROL

| Version | Date | Author | Changes |
|---|---|---|---|
| 1.0 | 2026-05-15 | System Developer | Initial design document |

**End of Document**
