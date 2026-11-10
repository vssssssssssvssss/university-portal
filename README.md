# university-portal
University Student Service Portal — B.Tech CSE Project
# UniPortal: University Student Service Portal

Students log in to see results and notices. Coordinators add marks and post notices.

## Team and file ownership
| Person | Role | Files |
|---|---|---|
| 1 | Backend | app.py, database.py, create_db.py, add_test_data.py |
| 2 | CSS | static/style.css |
| 3 | Core pages | templates/base.html, login.html, student/dashboard.html, student/profile.html |
| 4 | Feature pages | student/results.html, student/notices.html, all of templates/coordinator/ |

## Run it
```
pip install -r requirements.txt
python create_db.py
python add_test_data.py
python app.py
```
Open http://localhost:5000

## Test logins
- Student: 2023CS001 / student123
- Coordinator: coordinator1 / coord123

Stack: Python, Flask, SQLite, HTML, CSS.
