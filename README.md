# GFA School Management System

A comprehensive web-based School Management System for Junior Secondary School (JSS) and Senior Secondary School (SSS).

## Features

### 1. Student Registration & Management
- Complete student profile with personal, contact, and academic information
- Auto-generated admission numbers
- Parent/Guardian information tracking
- Student status management (Active, Suspended, Withdrawn, Graduated)
- Photo upload capability

### 2. Result Processing
- **Per-term result entry**: C.A (30 marks) + Exam (70 marks) = Total (100 marks)
- **Automatic grade calculation** using Nigerian grading system:
  - A1: 75-100 (Excellent, 5.0 pts)
  - B2: 70-74 (Very Good, 4.5 pts)
  - B3: 65-69 (Good, 4.0 pts)
  - C4: 60-64 (Credit, 3.75 pts)
  - C5: 55-59 (Credit, 3.25 pts)
  - C6: 50-54 (Credit, 3.0 pts)
  - D7: 45-49 (Pass, 2.0 pts)
  - E8: 40-44 (Pass, 1.0 pt)
  - F9: 0-39 (Fail, 0.0 pt)
- **Position calculation** per subject and overall class ranking
- **Session aggregation**: Combines First, Second, and Third term results
- **Promotion status** tracking

### 3. Subject Allocation
- JSS: 15 subjects (Core and Elective)
- SSS Science: 14 subjects (Physics, Chemistry, Biology, etc.)
- SSS Commercial: 13 subjects (Accounting, Commerce, Economics, etc.)
- SSS Arts: 14 subjects (Literature, Government, CRK, etc.)
- Subject-teacher assignment
- Student subject enrollment for electives

### 4. Psychomotor & Affective Assessment
- Psychomotor Skills: Handwriting, Verbal Fluency, Sports, Handling Tools, Drawing & Painting, Musical Skills
- Affective Disposition: Punctuality, Neatness, Politeness, Attitude to Work, Attentiveness, Speaking/Handwriting
- 5-point rating scale (5=Excellent to 1=Very Poor)

### 5. Attendance Management
- Track school days opened
- Record present, absent, and late attendance
- Per-term attendance summary

### 6. School Fees Management
- Fee structure setup per class/department/session/term
- Multiple fee types: Tuition, Examination, Sports, Library, Development Levy, PTA, Medical
- Payment recording with multiple payment methods
- Balance tracking and fee status monitoring

### 7. Report Card Generation
- Comprehensive report cards with all academic data
- Printable format with school header
- PDF download capability
- Class teacher and principal comments
- Achievement box for special recognition

### 8. Role-Based Access Control
- **Admin**: Full system access
- **Principal**: Academic oversight, comments, approvals
- **Teacher**: Result entry, assessments, attendance
- **Bursar**: Fee management, payments
- **Student/Parent**: View-only access to records

## Technology Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login with Werkzeug security
- **Frontend**: Bootstrap 5, Font Awesome, jQuery
- **PDF Generation**: ReportLab

## Installation

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip

### Setup Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd school_management_system
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create PostgreSQL database:
```bash
createdb gfa_school_db
```

5. Configure environment variables (optional):
```bash
export SECRET_KEY='your-secret-key'
export DATABASE_URL='postgresql://user:password@localhost/gfa_school_db'
```

6. Initialize database:
```bash
python app.py
```
The database will be automatically created on first run.

7. Access the application:
- URL: http://localhost:5000
- Default login: admin / admin123

## Database Schema

The system uses a comprehensive relational database with the following main tables:

- `users` - Authentication and roles
- `staff` - Teacher and administrative staff records
- `students` - Complete student profiles
- `classes` - JSS 1-3 and SSS 1-3 classes
- `departments` - JSS, Science, Commercial, Arts
- `subjects` - All academic subjects
- `class_subjects` - Subject allocation to classes
- `student_subjects` - Student elective enrollment
- `term_results` - Per-subject per-term scores
- `session_results` - Aggregated session-wide results
- `psychomotor_assessments` - Skills ratings
- `affective_assessments` - Behavior ratings
- `attendance` - Attendance records
- `school_fees` - Fee structures
- `fee_payments` - Payment records
- `result_comments` - Teacher and principal comments

## Usage Guide

### 1. Initial Setup
1. Login as admin (default: admin/admin123)
2. Go to Settings to configure school information
3. Create academic sessions and terms
4. Add staff members and assign roles
5. Setup classes and assign class teachers

### 2. Student Registration
1. Navigate to Students > Register Student
2. Fill in personal, contact, and academic information
3. System auto-generates admission number
4. Assign student to class and department (for SSS)

### 3. Result Entry
1. Go to Academics > Result Entry
2. Select class, subject, session, and term
3. Enter C.A and Exam scores for each student
4. System automatically calculates total, grade, and remark
5. Calculate positions after all results are entered

### 4. Report Cards
1. View results and click "Report Card" for any student
2. Print or download PDF version
3. Class teacher and principal can add comments

### 5. Fee Management
1. Setup fee structures per class/session/term
2. Record payments with reference numbers
3. Track balances and payment history

## Security Features

- Password hashing with Werkzeug
- Role-based access control
- CSRF protection
- Session management
- Input validation
- SQL injection prevention via SQLAlchemy ORM

## License

This project is proprietary software for GFA Secondary School.

## Support

For technical support, contact the system administrator.

---

**Developed for GFA Secondary School - JSS & SSS Administration**
