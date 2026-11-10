import sqlite3
from database import DB_PATH


def create_database():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'coordinator')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT NOT NULL UNIQUE,
            branch TEXT NOT NULL,
            semester INTEGER NOT NULL,
            batch_year TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            user_id INTEGER UNIQUE,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL,
            subject_code TEXT NOT NULL UNIQUE,
            semester INTEGER NOT NULL,
            max_marks INTEGER NOT NULL DEFAULT 100
        );

        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            marks_obtained INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            academic_year TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            UNIQUE(student_id, subject_id, semester, academic_year)
        );

        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            posted_by INTEGER NOT NULL,
            posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (posted_by) REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()
    print('Database created: users, students, subjects, results, announcements')


if __name__ == '__main__':
    create_database()
