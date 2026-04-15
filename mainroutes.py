from flask import session, Blueprint, render_template, request, redirect
from tools import get_db_connection


main = Blueprint("main", __name__)

@main.route("/")
def landing():
    return render_template("main/landing.html")


@main.route("/register")
def register():
    return render_template("main/register.html")


@main.route("/register-input", methods=["POST"])
def register_input():
    email = request.form.get("email")
    name = request.form.get("name")
    password = request.form.get("password")
    password_confirm = request.form.get("password-confirm")

    if password == password_confirm:
        password = password.encode("utf-8").hex()
        conn, cur = get_db_connection()

        cur.execute(f"SELECT 1 FROM users WHERE email = '{email}'")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"INSERT INTO users (email, name, password_md5) VALUES ('{email}', '{name}', '{password}')")
            conn.commit()

            cur.execute(f"SELECT id FROM users WHERE email = '{email}'")
            row = cur.fetchone()
            session["id"] = row["id"]
        else:
            return redirect("/?error=user-exists")
        conn.close()

    conn.close()

    return redirect("/logs")


@main.route("/login")
def login():
    return render_template("main/login.html")


@main.route("/login-input", methods=["POST"])
def login_input():
    email = request.form.get("email")
    password = request.form.get("password")

    conn, cur = get_db_connection()
    cur.execute(f"SELECT id, password_md5 FROM users WHERE email = '{email}'")
    row = cur.fetchone()
    id = row["id"]
    password_md5 = row["password_md5"]
    conn.close()
    
    if password_md5:
        if password.encode("utf-8").hex() == password_md5:
            session["id"] = id
    
            return redirect("/")
    return redirect("/login?error=not-found")