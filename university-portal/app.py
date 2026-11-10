from functools import wraps

from flask import Flask, render_template, request, redirect, session
from werkzeug.security import check_password_hash

import database as db

app = Flask(__name__)
# Signs the session cookie. Change this to your own random string.
app.secret_key = 'change-this-secret-key-before-submission'

HOME = {'student': '/student/dashboard', 'coordinator': '/coordinator/dashboard'}


def role_required(role):
    """Protect a route: only a logged-in user with this role may open it."""
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if session.get('role') != role:
                return redirect('/')
            return view(*args, **kwargs)
        return wrapper
    return decorator


def current_student():
    """The student profile of whoever is logged in (used by every student page)."""
    return db.get_student_by_user_id(session['user_id'])


# ---------- login and logout ----------
@app.route('/')
def home():
    if session.get('role') in HOME:
        return redirect(HOME[session['role']])
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    if not username or not password:
        return render_template('login.html', error='Enter both your roll number and password.')

    user = db.get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        session.clear()
        session['user_id'] = user['id']
        session['role'] = user['role']
        session['username'] = user['username']
        return redirect(HOME[user['role']])
    return render_template('login.html', error='Wrong roll number or password. Try again.')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---------- student pages ----------
@app.route('/student/dashboard')
@role_required('student')
def student_dashboard():
    return render_template('student/dashboard.html', student=current_student(),
                           recent_notices=db.get_active_announcements(limit=3))


@app.route('/student/results')
@role_required('student')
def student_results():
    student = current_student()
    selected = request.args.get('semester', type=int)
    processed, overall, passed, total = db.calculate_result_stats(
        db.get_student_results(student['id'], selected))
    summary = db.generate_result_summary(overall, passed, total) if processed else None
    semesters = sorted({r['semester'] for r in db.get_student_results(student['id'])})
    return render_template('student/results.html', student=student, results=processed,
                           overall=overall, passed=passed, total=total, summary=summary,
                           semesters=semesters, selected_semester=selected)


@app.route('/student/notices')
@role_required('student')
def student_notices():
    return render_template('student/notices.html', student=current_student(),
                           notices=db.get_active_announcements())


@app.route('/student/profile')
@role_required('student')
def student_profile():
    return render_template('student/profile.html', student=current_student())


# ---------- coordinator pages ----------
@app.route('/coordinator/dashboard')
@role_required('coordinator')
def coordinator_dashboard():
    return render_template('coordinator/dashboard.html',
                           total_students=len(db.get_all_students()),
                           total_notices=len(db.get_active_announcements()))


@app.route('/coordinator/add-result', methods=['GET', 'POST'])
@role_required('coordinator')
def add_result():
    message = error = None
    if request.method == 'POST':
        f = request.form
        try:
            student_id, subject_id = int(f['student_id']), int(f['subject_id'])
            marks, semester = int(f['marks']), int(f['semester'])
            year = f['academic_year'].strip()
            subject = db.get_subject(subject_id)
            if not year or subject is None:
                error = 'Fill in every field.'
            elif not 1 <= semester <= 8:
                error = 'Semester must be between 1 and 8.'
            elif not 0 <= marks <= subject['max_marks']:
                error = 'Marks must be between 0 and %d for this subject.' % subject['max_marks']
            else:
                action = db.add_or_update_result(student_id, subject_id, marks, semester, year)
                message = 'Result %s.' % action
        except (KeyError, ValueError):
            error = 'Fill in every field with valid numbers.'
    return render_template('coordinator/add_result.html', students=db.get_all_students(),
                           subjects=db.get_all_subjects(), message=message, error=error)


@app.route('/coordinator/post-notice', methods=['GET', 'POST'])
@role_required('coordinator')
def post_notice():
    message = error = None
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        if not title or not content:
            error = 'Enter both a title and the notice text.'
        else:
            db.post_announcement(title, content, session['user_id'])
            message = 'Notice posted. Students can see it now.'
    return render_template('coordinator/post_notice.html', message=message, error=error)


@app.route('/coordinator/students')
@role_required('coordinator')
def view_students():
    return render_template('coordinator/view_students.html', students=db.get_all_students())


if __name__ == '__main__':
    app.run(debug=True)
