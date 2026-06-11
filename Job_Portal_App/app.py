from flask import Flask, render_template, url_for, request, session, redirect, g
import secrets
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
DATABASE = 'jobs.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'seeker'
            )
        ''')
        # Added category and salary
        db.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                salary TEXT NOT NULL,
                employer_id INTEGER NOT NULL
            )
        ''')
        # PHASE 5: New applications table
        db.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                job_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # PHASE 6: Inject default admin account if it doesn't exist
        cursor = db.execute('SELECT id FROM users WHERE role = "admin"')
        if not cursor.fetchone():
            hashed_pw = generate_password_hash("admin123")
            db.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)', 
                       ("System Admin", "admin@admin.com", hashed_pw, "admin"))
            
        db.commit()

init_db()

# --- HELPER FUNCTION FOR ADMIN ---
def is_admin():
    user = session.get("user")
    return user and user.get("role") == "admin"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        role = request.form.get("role")
        
        if not all([name, email, password, confirm, role]):
            error = "All fields are required!"
        elif password != confirm:
            error = "Passwords do not match!"
        else:
            db = get_db()
            cursor = db.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone() is not None:
                error = "Email is already registered!"
            else:
                hashed_pw = generate_password_hash(password)
                cursor = db.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)', 
                                    (name, email, hashed_pw, role))
                db.commit()
                session["user"] = {"id": cursor.lastrowid, "name": name, "email": email, "role": role}
                return redirect(url_for("dashboard"))
                
    return render_template("register.html", error_msg=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if not email or not password:
            error = "Email and password are required!"
        else:
            db = get_db()
            cursor = db.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            
            if user is None or not check_password_hash(user['password'], password):
                error = "Invalid email or password!"
            else:
                session["user"] = {"id": user['id'], "name": user['name'], "email": user['email'], "role": user['role']}
                return redirect(url_for("dashboard"))
                
    return render_template("login.html", error_msg=error)

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
        
    # Redirect Admin to their specific panel
    if user.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))
        
    db = get_db()
    cursor = db.execute('SELECT * FROM jobs ORDER BY id DESC LIMIT 5')
    jobs = cursor.fetchall()
    
    return render_template("dashboard.html", name=user.get("name"), email=user.get("email"), jobs=jobs)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# ==========================================
# PHASE 4: EMPLOYER ROUTES (Updated with Category/Salary)
# ==========================================
@app.route("/post-job", methods=["GET", "POST"])
def post_job():
    user = session.get("user")
    if not user or user.get("role") != "employer":
        return redirect(url_for("dashboard"))
        
    if request.method == "POST":
        title = request.form.get("title")
        company = request.form.get("company")
        location = request.form.get("location")
        category = request.form.get("category")
        salary = request.form.get("salary")
        description = request.form.get("description")
        
        db = get_db()
        db.execute('INSERT INTO jobs (title, company, location, category, salary, description, employer_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (title, company, location, category, salary, description, user['id']))
        db.commit()
        return redirect(url_for("my_jobs"))
        
    return render_template("post_job.html", job=None)

@app.route("/my-jobs")
def my_jobs():
    user = session.get("user")
    if not user or user.get("role") != "employer":
        return redirect(url_for("dashboard"))
        
    db = get_db()
    cursor = db.execute('SELECT * FROM jobs WHERE employer_id = ? ORDER BY id DESC', (user['id'],))
    jobs = cursor.fetchall()
    return render_template("my_jobs.html", jobs=jobs)

@app.route("/edit-job/<int:id>", methods=["GET", "POST"])
def edit_job(id):
    user = session.get("user")
    if not user or user.get("role") != "employer":
        return redirect(url_for("dashboard"))
        
    db = get_db()
    if request.method == "GET":
        cursor = db.execute('SELECT * FROM jobs WHERE id = ? AND employer_id = ?', (id, user['id']))
        job = cursor.fetchone()
        if not job:
            return redirect(url_for("my_jobs"))
        return render_template("post_job.html", job=job)
        
    if request.method == "POST":
        title = request.form.get("title")
        company = request.form.get("company")
        location = request.form.get("location")
        category = request.form.get("category")
        salary = request.form.get("salary")
        description = request.form.get("description")
        
        db.execute('UPDATE jobs SET title=?, company=?, location=?, category=?, salary=?, description=? WHERE id=? AND employer_id=?',
                   (title, company, location, category, salary, description, id, user['id']))
        db.commit()
        return redirect(url_for("my_jobs"))

@app.route("/delete-job/<int:id>", methods=["POST"])
def delete_job(id):
    user = session.get("user")
    if not user or user.get("role") != "employer":
        return redirect(url_for("dashboard"))
        
    db = get_db()
    db.execute('DELETE FROM jobs WHERE id = ? AND employer_id = ?', (id, user['id']))
    db.commit()
    return redirect(url_for("my_jobs"))

# ==========================================
# PHASE 5: SEEKER SEARCH & APPLY ROUTES
# ==========================================
@app.route("/jobs")
def search_jobs():
    db = get_db()
    
    # Base query
    query = "SELECT * FROM jobs WHERE 1=1"
    params = []
    
    # Get filter values from the URL (GET request)
    keyword = request.args.get("keyword", "").strip()
    location = request.args.get("location", "").strip()
    category = request.args.get("category", "").strip()
    
    # Apply SQL filters dynamically
    if keyword:
        query += " AND (title LIKE ? OR company LIKE ? OR description LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"])
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if category:
        query += " AND category = ?"
        params.append(category)
        
    query += " ORDER BY id DESC"
    
    cursor = db.execute(query, params)
    jobs = cursor.fetchall()
    
    return render_template("jobs.html", jobs=jobs, keyword=keyword, location=location, category=category)

@app.route("/job/<int:id>")
def job_detail(id):
    db = get_db()
    cursor = db.execute('SELECT * FROM jobs WHERE id = ?', (id,))
    job = cursor.fetchone()
    
    if not job:
        return "Job not found", 404
        
    # Check if the current user has already applied
    has_applied = False
    user = session.get("user")
    if user and user.get("role") == "seeker":
        app_cursor = db.execute('SELECT id FROM applications WHERE user_id = ? AND job_id = ?', (user['id'], id))
        if app_cursor.fetchone():
            has_applied = True
            
    return render_template("job_detail.html", job=job, has_applied=has_applied)

@app.route("/apply/<int:job_id>", methods=["POST"])
def apply(job_id):
    user = session.get("user")
    # Only seekers can apply
    if not user or user.get("role") != "seeker":
        return redirect(url_for("login"))
        
    db = get_db()
    # Prevent duplicate applications
    cursor = db.execute('SELECT id FROM applications WHERE user_id = ? AND job_id = ?', (user['id'], job_id))
    if not cursor.fetchone():
        db.execute('INSERT INTO applications (user_id, job_id) VALUES (?, ?)', (user['id'], job_id))
        db.commit()
        
    return redirect(url_for("job_detail", id=job_id))


@app.route("/applied-jobs")
def applied_jobs():
    user = session.get("user")
    # Security check: only seekers can access this route
    if not user or user.get("role") != "seeker":
        return redirect(url_for("dashboard"))
        
    db = get_db()
    
    # Join jobs and applications tables to get full details
    query = '''
        SELECT jobs.*, applications.status, applications.applied_at 
        FROM jobs 
        JOIN applications ON jobs.id = applications.job_id 
        WHERE applications.user_id = ? 
        ORDER BY applications.applied_at DESC
    '''
    cursor = db.execute(query, (user['id'],))
    applied_jobs_list = cursor.fetchall()
    
    return render_template("applied_jobs.html", applied_jobs=applied_jobs_list)

# ==========================================
# PHASE 6: ADMIN PANEL ROUTES
# ==========================================

@app.route("/admin/dashboard")
def admin_dashboard():
    if not is_admin():
        return redirect(url_for("dashboard"))
        
    db = get_db()
    user_count = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    job_count = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    app_count = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]
    
    return render_template("admin_dashboard.html", user_count=user_count, job_count=job_count, app_count=app_count)

@app.route("/admin/users")
def admin_users():
    if not is_admin():
        return redirect(url_for("dashboard"))
        
    db = get_db()
    users = db.execute("SELECT id, name, email, role FROM users ORDER BY id DESC").fetchall()
    
    return render_template("admin_users.html", users=users)

@app.route("/admin/jobs", methods=["GET", "POST"])
def admin_jobs():
    if not is_admin():
        return redirect(url_for("dashboard"))
        
    db = get_db()
    
    # Handle moderation deletion
    if request.method == "POST":
        job_id = request.form.get("job_id")
        db.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        # Clean up associated applications when a job is deleted
        db.execute("DELETE FROM applications WHERE job_id = ?", (job_id,))
        db.commit()
        return redirect(url_for("admin_jobs"))
        
    jobs = db.execute('''
        SELECT jobs.*, users.name as employer_name 
        FROM jobs 
        JOIN users ON jobs.employer_id = users.id 
        ORDER BY jobs.id DESC
    ''').fetchall()
    
    return render_template("admin_jobs.html", jobs=jobs)

@app.route("/admin/applications", methods=["GET", "POST"])
def admin_applications():
    if not is_admin():
        return redirect(url_for("dashboard"))
        
    db = get_db()
    
    # Handle moderation deletion
    if request.method == "POST":
        app_id = request.form.get("app_id")
        db.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        db.commit()
        return redirect(url_for("admin_applications"))
        
    apps = db.execute('''
        SELECT applications.*, users.name as applicant_name, jobs.title as job_title 
        FROM applications 
        JOIN users ON applications.user_id = users.id 
        JOIN jobs ON applications.job_id = jobs.id 
        ORDER BY applications.id DESC
    ''').fetchall()
    
    return render_template("admin_applications.html", apps=apps)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5001)