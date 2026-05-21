-- ============================================================
-- GFA SCHOOL MANAGEMENT SYSTEM - COMPLETE DATABASE SCHEMA
-- For JSS and SSS (Junior & Senior Secondary School)
-- ============================================================

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS fee_payments CASCADE;
DROP TABLE IF EXISTS school_fees CASCADE;
DROP TABLE IF EXISTS affective_assessments CASCADE;
DROP TABLE IF EXISTS psychomotor_assessments CASCADE;
DROP TABLE IF EXISTS result_comments CASCADE;
DROP TABLE IF EXISTS term_results CASCADE;
DROP TABLE IF EXISTS session_results CASCADE;
DROP TABLE IF EXISTS student_subjects CASCADE;
DROP TABLE IF EXISTS class_subjects CASCADE;
DROP TABLE IF EXISTS subjects CASCADE;
DROP TABLE IF EXISTS attendance CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS class_teachers CASCADE;
DROP TABLE IF EXISTS classes CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;
DROP TABLE IF EXISTS terms CASCADE;
DROP TABLE IF EXISTS staff CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS settings CASCADE;

-- ============================================================
-- 1. CORE CONFIGURATION TABLES
-- ============================================================

CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    school_name VARCHAR(255) NOT NULL DEFAULT 'GFA Secondary School',
    school_address TEXT,
    school_phone VARCHAR(50),
    school_email VARCHAR(100),
    school_motto TEXT,
    current_session VARCHAR(20),
    current_term INTEGER,
    ca_max_score INTEGER DEFAULT 30,
    exam_max_score INTEGER DEFAULT 70,
    pass_mark INTEGER DEFAULT 40,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE terms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    term_number INTEGER NOT NULL CHECK (term_number BETWEEN 1 AND 3),
    description VARCHAR(50)
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. USER MANAGEMENT & ROLES
-- ============================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'principal', 'teacher', 'bursar', 'student', 'parent')),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. STAFF & DEPARTMENTS
-- ============================================================

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE,
    description TEXT,
    head_of_department INTEGER
);

CREATE TABLE staff (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    staff_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    other_names VARCHAR(50),
    sex VARCHAR(10) CHECK (sex IN ('Male', 'Female')),
    date_of_birth DATE,
    qualification VARCHAR(100),
    department_id INTEGER REFERENCES departments(id),
    designation VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    date_employed DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE departments ADD CONSTRAINT fk_hod 
    FOREIGN KEY (head_of_department) REFERENCES staff(id);

-- ============================================================
-- 4. CLASSES & STREAMS
-- ============================================================

CREATE TABLE classes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    level VARCHAR(10) NOT NULL CHECK (level IN ('JSS', 'SSS')),
    department_id INTEGER REFERENCES departments(id),
    class_teacher_id INTEGER REFERENCES staff(id),
    capacity INTEGER DEFAULT 40,
    room VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE class_teachers (
    id SERIAL PRIMARY KEY,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    teacher_id INTEGER REFERENCES staff(id),
    session_id INTEGER REFERENCES sessions(id),
    term_id INTEGER REFERENCES terms(id),
    assigned_date DATE DEFAULT CURRENT_DATE,
    is_current BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- 5. STUDENTS
-- ============================================================

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    admission_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    other_names VARCHAR(50),
    sex VARCHAR(10) CHECK (sex IN ('Male', 'Female')),
    date_of_birth DATE,
    place_of_birth VARCHAR(100),
    state_of_origin VARCHAR(50),
    local_government VARCHAR(50),
    nationality VARCHAR(50) DEFAULT 'Nigerian',
    religion VARCHAR(30),
    blood_group VARCHAR(5),
    genotype VARCHAR(5),
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100),
    parent_name VARCHAR(100),
    parent_phone VARCHAR(20),
    parent_email VARCHAR(100),
    parent_address TEXT,
    parent_occupation VARCHAR(50),
    class_id INTEGER REFERENCES classes(id),
    department_id INTEGER REFERENCES departments(id),
    date_admitted DATE,
    previous_school VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'withdrawn', 'graduated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 6. SUBJECTS & ALLOCATION
-- ============================================================

CREATE TABLE subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE,
    category VARCHAR(30),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE class_subjects (
    id SERIAL PRIMARY KEY,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id),
    is_compulsory BOOLEAN DEFAULT TRUE,
    teacher_id INTEGER REFERENCES staff(id),
    session_id INTEGER REFERENCES sessions(id),
    UNIQUE(class_id, subject_id, department_id, session_id)
);

CREATE TABLE student_subjects (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    class_id INTEGER REFERENCES classes(id),
    session_id INTEGER REFERENCES sessions(id),
    is_active BOOLEAN DEFAULT TRUE,
    enrolled_date DATE DEFAULT CURRENT_DATE,
    UNIQUE(student_id, subject_id, session_id)
);

-- ============================================================
-- 7. ATTENDANCE
-- ============================================================

CREATE TABLE attendance (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    class_id INTEGER REFERENCES classes(id),
    session_id INTEGER REFERENCES sessions(id),
    term_id INTEGER REFERENCES terms(id),
    school_opened INTEGER DEFAULT 0,
    times_present INTEGER DEFAULT 0,
    times_absent INTEGER DEFAULT 0,
    times_late INTEGER DEFAULT 0,
    vacates_on DATE,
    resumes_on DATE,
    updated_by INTEGER REFERENCES staff(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, session_id, term_id)
);

-- ============================================================
-- 8. ACADEMIC RESULTS
-- ============================================================

CREATE TABLE term_results (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    class_id INTEGER REFERENCES classes(id),
    session_id INTEGER REFERENCES sessions(id),
    term_id INTEGER REFERENCES terms(id),
    ca_score INTEGER CHECK (ca_score BETWEEN 0 AND 30),
    exam_score INTEGER CHECK (exam_score BETWEEN 0 AND 70),
    total_score INTEGER GENERATED ALWAYS AS (ca_score + exam_score) STORED,
    grade VARCHAR(5),
    grade_point DECIMAL(3,2),
    remark VARCHAR(20),
    subject_position INTEGER,
    entered_by INTEGER REFERENCES staff(id),
    entered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_by INTEGER REFERENCES staff(id),
    verified_at TIMESTAMP,
    UNIQUE(student_id, subject_id, session_id, term_id)
);

CREATE TABLE session_results (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    class_id INTEGER REFERENCES classes(id),
    session_id INTEGER REFERENCES sessions(id),
    first_term_total INTEGER,
    first_term_avg DECIMAL(5,2),
    first_term_grade VARCHAR(5),
    second_term_total INTEGER,
    second_term_avg DECIMAL(5,2),
    second_term_grade VARCHAR(5),
    third_term_total INTEGER,
    third_term_avg DECIMAL(5,2),
    third_term_grade VARCHAR(5),
    sessional_total INTEGER,
    sessional_avg DECIMAL(5,2),
    sessional_grade VARCHAR(5),
    sessional_position INTEGER,
    class_highest DECIMAL(5,2),
    class_lowest DECIMAL(5,2),
    class_average DECIMAL(5,2),
    year_highest DECIMAL(5,2),
    year_lowest DECIMAL(5,2),
    year_average DECIMAL(5,2),
    year_position INTEGER,
    total_obtainable INTEGER,
    total_score INTEGER,
    grade_point DECIMAL(3,2),
    promoted_to INTEGER REFERENCES classes(id),
    promotion_status VARCHAR(20) DEFAULT 'pending' CHECK (promotion_status IN ('pending', 'promoted', 'repeat', 'withdrawn')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, session_id)
);

-- ============================================================
-- 9. PSYCHOMOTOR & AFFECTIVE ASSESSMENTS
-- ============================================================

CREATE TABLE psychomotor_assessments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES sessions(id),
    term_id INTEGER REFERENCES terms(id),
    handwriting INTEGER CHECK (handwriting BETWEEN 1 AND 5),
    verbal_fluency INTEGER CHECK (verbal_fluency BETWEEN 1 AND 5),
    sports INTEGER CHECK (sports BETWEEN 1 AND 5),
    handling_tools INTEGER CHECK (handling_tools BETWEEN 1 AND 5),
    drawing_painting INTEGER CHECK (drawing_painting BETWEEN 1 AND 5),
    musical_skills INTEGER CHECK (musical_skills BETWEEN 1 AND 5),
    assessed_by INTEGER REFERENCES staff(id),
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, session_id, term_id)
);

CREATE TABLE affective_assessments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES sessions(id),
    term_id INTEGER REFERENCES terms(id),
    punctuality INTEGER CHECK (punctuality BETWEEN 1 AND 5),
    neatness INTEGER CHECK (neatness BETWEEN 1 AND 5),
    politeness INTEGER CHECK (politeness BETWEEN 1 AND 5),
    attitude_to_work INTEGER CHECK (attitude_to_work BETWEEN 1 AND 5),
    attentiveness INTEGER CHECK (attentiveness BETWEEN 1 AND 5),
    speaking_handwriting INTEGER CHECK (speaking_handwriting BETWEEN 1 AND 5),
    assessed_by INTEGER REFERENCES staff(id),
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, session_id, term_id)
);

-- ============================================================
-- 10. COMMENTS & ACHIEVEMENTS
-- ============================================================

CREATE TABLE result_comments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES sessions(id),
    term_id INTEGER REFERENCES terms(id),
    class_teacher_comment TEXT,
    principal_comment TEXT,
    achievement_box TEXT,
    class_teacher_id INTEGER REFERENCES staff(id),
    principal_id INTEGER REFERENCES staff(id),
    teacher_signed_at TIMESTAMP,
    principal_signed_at TIMESTAMP,
    UNIQUE(student_id, session_id, term_id)
);

-- ============================================================
-- 11. SCHOOL FEES MANAGEMENT
-- ============================================================

CREATE TABLE school_fees (
    id SERIAL PRIMARY KEY,
    class_id INTEGER REFERENCES classes(id),
    department_id INTEGER REFERENCES departments(id),
    session_id INTEGER REFERENCES sessions(id),
    term_id INTEGER REFERENCES terms(id),
    fee_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    due_date DATE,
    is_mandatory BOOLEAN DEFAULT TRUE,
    created_by INTEGER REFERENCES staff(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fee_payments (
    id SERIAL PRIMARY KEY,
    student_id INTEGER REFERENCES students(id) ON DELETE CASCADE,
    fee_id INTEGER REFERENCES school_fees(id),
    amount_paid DECIMAL(10,2) NOT NULL,
    amount_due DECIMAL(10,2),
    balance DECIMAL(10,2) GENERATED ALWAYS AS (amount_due - amount_paid) STORED,
    payment_method VARCHAR(30),
    transaction_reference VARCHAR(100),
    payment_date DATE DEFAULT CURRENT_DATE,
    received_by INTEGER REFERENCES staff(id),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX idx_students_class ON students(class_id);
CREATE INDEX idx_students_admission ON students(admission_number);
CREATE INDEX idx_term_results_student ON term_results(student_id);
CREATE INDEX idx_term_results_session ON term_results(session_id, term_id);
CREATE INDEX idx_term_results_class ON term_results(class_id);
CREATE INDEX idx_session_results_student ON session_results(student_id);
CREATE INDEX idx_attendance_student ON attendance(student_id, session_id, term_id);
CREATE INDEX idx_fee_payments_student ON fee_payments(student_id);
CREATE INDEX idx_class_subjects_class ON class_subjects(class_id);

-- ============================================================
-- SEED DATA
-- ============================================================

INSERT INTO terms (name, term_number, description) VALUES
    ('First Term', 1, 'First Academic Term'),
    ('Second Term', 2, 'Second Academic Term'),
    ('Third Term', 3, 'Third Academic Term');

INSERT INTO departments (name, code, description) VALUES
    ('JSS (Junior Secondary)', 'JSS', 'Junior Secondary School Department'),
    ('Science', 'SCI', 'Science Department - Physics, Chemistry, Biology'),
    ('Commercial', 'COM', 'Commercial Department - Accounting, Commerce, Economics'),
    ('Arts', 'ART', 'Arts Department - Literature, Government, CRK');

INSERT INTO settings (school_name, current_session, current_term, ca_max_score, exam_max_score) VALUES
    ('GFA Secondary School', '2025/2026', 1, 30, 70);

INSERT INTO subjects (name, code, category) VALUES
    ('Religious and Moral Instructions', 'RMI', 'Core'),
    ('Computer Study', 'CMP', 'Core'),
    ('Business Study', 'BUS', 'Elective'),
    ('Cultural and Creative Arts/Music', 'CCA', 'Elective'),
    ('Basic Technology', 'BAS', 'Core'),
    ('Civic Education', 'CIV', 'Core'),
    ('Yoruba Language', 'YOR', 'Core'),
    ('English Language', 'ENG', 'Core'),
    ('Mathematics', 'MAT', 'Core'),
    ('Basic Science', 'BSC', 'Core'),
    ('Prevocational Studies', 'PVS', 'Elective'),
    ('National Values Education', 'NVE', 'Core'),
    ('Physical Education', 'PED', 'Core'),
    ('French', 'FRE', 'Elective'),
    ('Christian Religious Knowledge', 'CRK', 'Core'),
    ('Physics', 'PHY', 'Core'),
    ('Chemistry', 'CHM', 'Core'),
    ('Biology', 'BIO', 'Core'),
    ('Animal Husbandry', 'AHB', 'Elective'),
    ('Data Processing', 'DAP', 'Elective'),
    ('Agricultural Science', 'AGR', 'Elective'),
    ('Further Mathematics', 'FMA', 'Elective'),
    ('Financial Accounting', 'FAC', 'Core'),
    ('Commerce', 'COM', 'Core'),
    ('Economics', 'ECO', 'Core'),
    ('Geography', 'GEO', 'Elective'),
    ('Government', 'GOV', 'Core'),
    ('Literature-in-English', 'LIT', 'Core');

INSERT INTO classes (name, level, department_id, capacity) VALUES
    ('JSS 1', 'JSS', 1, 40),
    ('JSS 2', 'JSS', 1, 40),
    ('JSS 3', 'JSS', 1, 40),
    ('SSS 1', 'SSS', NULL, 40),
    ('SSS 2', 'SSS', NULL, 40),
    ('SSS 3', 'SSS', NULL, 40);

INSERT INTO users (username, password_hash, email, role) VALUES
    ('admin', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin@gfaschool.edu.ng', 'admin');
