# 🚀 FindJob - Professional Job Portal

FindJob is a full-stack, responsive web application built with Python and Flask. It serves as a dual-sided marketplace connecting job seekers with employers, featuring role-based access, job management, and an elegant Bootstrap 5 UI.

## ✨ Features

**For Job Seekers:**
* 🔍 **Smart Search:** Filter available jobs by keyword, location, and category.
* 📝 **One-Click Apply:** Submit applications directly to employers.
* 📊 **Application Tracker:** Monitor the real-time status of all submitted applications.

**For Employers:**
* 🏢 **Job Management:** Post, edit, and delete job listings.
* 💼 **Detailed Postings:** Specify salary ranges, categories, and locations.

**For Administrators:**
* ⚙️ **Control Panel:** Track total users, active jobs, and application metrics.
* 🛡️ **Moderation:** Delete flagged jobs, remove applications, and manage users.

## 🛠️ Tech Stack

* **Backend:** Python, Flask, Werkzeug (Password Hashing)
* **Frontend:** HTML5, CSS3, Bootstrap 5, Jinja2 Templating
* **Database:** SQLite3 (Relational tables for Users, Jobs, and Applications)
* **Architecture:** Monolithic MVC

## 🚀 Getting Started

### 1. Clone the repository
\`\`\`bash
git clone https://github.com/yourusername/FindJob.git
cd FindJob
\`\`\`

### 2. Set up a Virtual Environment (Optional but recommended)
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
\`\`\`

### 3. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Run the Application
\`\`\`bash
python app.py
\`\`\`
*The database (`jobs.db`) and a default Admin account will automatically be generated on the first run.*

### 5. Access the Portal
Open your web browser and navigate to: `http://127.0.0.1:5001`

**Default Admin Credentials:**
* **Email:** admin@admin.com
* **Password:** admin123

## 📁 Project Structure

\`\`\`text
FindJob:.
│   app.py
│   config.py
│   forms.py
│   jobs.db
│   models.py
│   README.md
│   requirements.txt
│   __init__.py
│   
├───instance
│       find_job.db
│       
├───routes
│   │   auth.py
│   │   __init__.py
│   │   
│   └───__pycache__
│           auth.cpython-313.pyc
│           __init__.cpython-313.pyc
│           
├───static
│   └───css
│           style.css
│           
├───templates
│       admin_applications.html
│       admin_dashboard.html
│       admin_jobs.html
│       admin_users.html
│       applied_jobs.html
│       base.html
│       dashboard.html
│       home.html
│       jobs.html
│       job_detail.html
│       login.html
│       my_jobs.html
│       post_job.html
│       register.html
│       
└───__pycache__
        config.cpython-313.pyc
        forms.cpython-313.pyc
        models.cpython-313.pyc
        __init__.cpython-313.pyc
\`\`\`

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.