import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')


def get_db():
    """Open a connection. row_factory lets us read columns by name: row['name']."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def query(sql, args=(), one=False):
    """Run a SELECT and return all rows (or just the first row if one=True)."""
    conn = get_db()
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    if one:
        return rows[0] if rows else None
    return rows


# ---- users and students ----
def get_user_by_username(username):
    return query('SELECT * FROM users WHERE username = ?', (username,), one=True)


def get_student_by_user_id(user_id):
    return query('SELECT * FROM students WHERE user_id = ?', (user_id,), one=True)


def get_all_students():
    return query('SELECT * FROM students ORDER BY roll_number')


# ---- subjects ----
def get_all_subjects():
    return query('SELECT * FROM subjects ORDER BY semester, subject_name')


def get_subject(subject_id):
    return query('SELECT * FROM subjects WHERE id = ?', (subject_id,), one=True)


# ---- results ----
def get_student_results(student_id, semester=None):
    """JOIN pulls the subject name and max marks in with each result row."""
    sql = '''SELECT r.marks_obtained, r.semester, r.academic_year,
                    s.subject_name, s.subject_code, s.max_marks
             FROM results r JOIN subjects s ON r.subject_id = s.id
             WHERE r.student_id = ?'''
    args = [student_id]
    if semester:
        sql += ' AND r.semester = ?'
        args.append(semester)
    sql += ' ORDER BY r.semester, s.subject_name'
    return query(sql, args)


def add_or_update_result(student_id, subject_id, marks, semester, academic_year):
    """Insert a result, or update it if that student already has one for this subject/term."""
    conn = get_db()
    where = 'student_id = ? AND subject_id = ? AND semester = ? AND academic_year = ?'
    key = (student_id, subject_id, semester, academic_year)
    exists = conn.execute('SELECT id FROM results WHERE ' + where, key).fetchone()
    if exists:
        conn.execute('UPDATE results SET marks_obtained = ? WHERE ' + where, (marks,) + key)
        action = 'updated'
    else:
        conn.execute('''INSERT INTO results
                        (student_id, subject_id, marks_obtained, semester, academic_year)
                        VALUES (?,?,?,?,?)''', (student_id, subject_id, marks, semester, academic_year))
        action = 'added'
    conn.commit()
    conn.close()
    return action


# ---- announcements ----
def get_active_announcements(limit=None):
    sql = '''SELECT a.id, a.title, a.content, a.posted_at, u.username AS posted_by
             FROM announcements a JOIN users u ON a.posted_by = u.id
             WHERE a.is_active = 1 ORDER BY a.posted_at DESC, a.id DESC'''
    if limit:
        sql += ' LIMIT %d' % int(limit)
    return query(sql)


def post_announcement(title, content, user_id):
    conn = get_db()
    conn.execute('INSERT INTO announcements (title, content, posted_by) VALUES (?,?,?)',
                 (title, content, user_id))
    conn.commit()
    conn.close()


# ---- calculations (plain Python, no database) ----
def calculate_result_stats(results):
    """Return (processed rows, overall %, subjects passed, total subjects). Pass mark is 40%."""
    processed, total_marks, total_max, passed = [], 0, 0, 0
    for r in results:
        marks, max_marks = r['marks_obtained'], r['max_marks']
        is_pass = marks >= max_marks * 0.40
        passed += is_pass
        total_marks += marks
        total_max += max_marks
        processed.append({
            'subject_name': r['subject_name'], 'subject_code': r['subject_code'],
            'marks': marks, 'max_marks': max_marks,
            'percentage': round(marks / max_marks * 100, 1),
            'status': 'Pass' if is_pass else 'Fail',
            'semester': r['semester'], 'academic_year': r['academic_year'],
        })
    overall = round(total_marks / total_max * 100, 1) if total_max else 0
    return processed, overall, passed, len(processed)


def generate_result_summary(overall, passed, total):
    """Turn the numbers into one plain-English paragraph."""
    failed = total - passed
    text = 'You passed %d of %d subjects with an overall percentage of %s%%. ' % (passed, total, overall)
    if failed:
        text += 'You failed %d subject%s, so focus on %s before the next exam. ' % (
            failed, 's' if failed > 1 else '', 'those' if failed > 1 else 'that one')
    if overall >= 75:
        text += 'Excellent performance this semester.'
    elif overall >= 60:
        text += 'Good performance, with room to improve.'
    elif overall >= 40:
        text += 'Average performance. Consistent effort will lift it.'
    else:
        text += 'This needs significant improvement. Please speak to your faculty.'
    return text
