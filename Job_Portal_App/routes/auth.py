from flask import flash, redirect, render_template_string, url_for
from flask_login import current_user, login_required, login_user, logout_user

from __init__ import db
from forms import LoginForm, RegistrationForm
from models import User

from . import auth_bp


def _dashboard_endpoint(role):
    return {
        "seeker": "auth.seeker_dashboard",
        "employer": "auth.employer_dashboard",
        "admin": "auth.admin_dashboard",
    }.get(role, "auth.dashboard")


def _render_auth_page(
    title,
    form,
    button_label,
    include_username=False,
    include_role=False,
    include_remember=False,
):
    return render_template_string(
        """
        <h1>{{ title }}</h1>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul>
              {% for message in messages %}
                <li>{{ message }}</li>
              {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <form method="post">
          {{ form.hidden_tag() }}
                    {% if include_username %}
                        <p>{{ form.username.label }} {{ form.username() }}</p>
                    {% endif %}
          <p>{{ form.email.label }} {{ form.email() }}</p>
          <p>{{ form.password.label }} {{ form.password() }}</p>
                    {% if include_role %}
            <p>{{ form.role.label }} {{ form.role() }}</p>
          {% endif %}
                    {% if include_remember %}
            <p>{{ form.remember() }} {{ form.remember.label }}</p>
          {% endif %}
          <p>{{ form.submit(value=button_label) }}</p>
        </form>
        """,
        title=title,
        form=form,
        button_label=button_label,
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if existing_user:
            flash("Username or email already exists.")
            return _render_auth_page(
                "Register",
                form,
                "Register",
                include_username=True,
                include_role=True,
            )

        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Registration successful.")
        return redirect(url_for(_dashboard_endpoint(user.role)))

    return _render_auth_page(
        "Register",
        form,
        "Register",
        include_username=True,
        include_role=True,
    )


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Logged in successfully.")
            return redirect(url_for(_dashboard_endpoint(user.role)))

        flash("Invalid email or password.")

    return _render_auth_page("Login", form, "Login", include_remember=True)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("auth.login"))


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return redirect(url_for(_dashboard_endpoint(current_user.role)))


@auth_bp.route("/seeker/dashboard")
@login_required
def seeker_dashboard():
    return render_template_string(
        """
        <h1>{{ current_user.dashboard_label() }}</h1>
        <p>Welcome, {{ current_user.username }}.</p>
        <p>Role: {{ current_user.role }}</p>
        <p><a href="{{ url_for('auth.logout') }}">Logout</a></p>
        """
    )


@auth_bp.route("/employer/dashboard")
@login_required
def employer_dashboard():
    return render_template_string(
        """
        <h1>{{ current_user.dashboard_label() }}</h1>
        <p>Welcome, {{ current_user.username }}.</p>
        <p>Role: {{ current_user.role }}</p>
        <p><a href="{{ url_for('auth.logout') }}">Logout</a></p>
        """
    )


@auth_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    return render_template_string(
        """
        <h1>{{ current_user.dashboard_label() }}</h1>
        <p>Welcome, {{ current_user.username }}.</p>
        <p>Role: {{ current_user.role }}</p>
        <p><a href="{{ url_for('auth.logout') }}">Logout</a></p>
        """
    )