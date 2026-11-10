import random
import sqlite3
from werkzeug.security import generate_password_hash
from database import DB_PATH

STUDENTS = [
    ('Rahul Sharma', '2023CS001'), ('Priya Patel', '2023CS002'),
    ('Amit Kumar', '2023CS003'), ('Sneha Verma', '2023CS004'),
    ('Rohan Singh', '2023CS005'), ('Ankit Sharma', '2023CS006'),
    ('Pooja Gupta', '2023CS007'), ('Vikram Yadav', '2023CS008'),
]
SUBJECTS = [
    ('Mathematics III', 'MA301'), ('Data Structures', 'CS301'),
    ('Computer Networks', 'CS302'), ('Operating Systems', 'CS303'),
    ('Theory of Computation', 'CS304'), ('Discrete Mathematics', 'CS305'),
]
NOTICES = [
    ('Mid semester exam schedule',
     'Mid semester exams run from November 25th to December 5th. Carry your college ID card to every exam.'),
    ('Library timing change',
     'The library is now open 8 AM to 9 PM on working days and 10 AM to 6 PM on weekends.'),
    ('Project submission reminder',
     'All semester projects must be submitted by November 20th through your department coordinator.'),
]


def one(cur, sql, args):
    return cur.execute(sql, args).fetchone()[0]


def add_test_data():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?,?,?)',
                ('coordinator1', generate_password_hash('coord123'), 'coordinator'))

    for i, (name, roll) in enumerate(STUDENTS, start=1):
        cur.execute('INSERT OR IGNORE INTO users (username, password_hash, role) VALUES (?,?,?)',
                    (roll, generate_password_hash('student123'), 'student'))
        uid = one(cur, 'SELECT id FROM users WHERE username = ?', (roll,))
        cur.execute('''INSERT OR IGNORE INTO students
                       (name, roll_number, branch, semester, batch_year, email, phone, user_id)
                       VALUES (?,?,?,?,?,?,?,?)''',
                    (name, roll, 'CSE', 3, '2023-27',
                     name.split()[0].lower() + '@college.edu', '98765432%02d' % i, uid))

    for name, code in SUBJECTS:
        cur.execute('INSERT OR IGNORE INTO subjects (subject_name, subject_code, semester, max_marks) VALUES (?,?,?,?)',
                    (name, code, 3, 100))

    rng = random.Random(42)  # same marks every run
    for _, roll in STUDENTS:
        sid = one(cur, 'SELECT id FROM students WHERE roll_number = ?', (roll,))
        for _, code in SUBJECTS:
            subid = one(cur, 'SELECT id FROM subjects WHERE subject_code = ?', (code,))
            cur.execute('''INSERT OR IGNORE INTO results
                           (student_id, subject_id, marks_obtained, semester, academic_year)
                           VALUES (?,?,?,?,?)''', (sid, subid, rng.randint(32, 94), 3, '2025-26'))

    if one(cur, 'SELECT COUNT(*) FROM announcements', ()) == 0:
        coord = one(cur, 'SELECT id FROM users WHERE username = ?', ('coordinator1',))
        for title, content in NOTICES:
            cur.execute('INSERT INTO announcements (title, content, posted_by) VALUES (?,?,?)',
                        (title, content, coord))

    conn.commit()
    conn.close()
    print('Test data added.')
    print('Student:     2023CS001 / student123')
    print('Coordinator: coordinator1 / coord123')


if __name__ == '__main__':
    add_test_data()
