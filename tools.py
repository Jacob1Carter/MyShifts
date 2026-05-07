import sqlite3
from functools import wraps
from flask import session, redirect


def get_db_connection():
    conn = sqlite3.connect("data/database.db")
    conn.row_factory = sqlite3.Row  # Enable row factory for dict-like access
    cur = conn.cursor()
    return conn, cur


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not session.get("id"):
            return redirect("/login")
        return func(*args, **kwargs)

    return decorated_view


def session_check():
    if not session.get("name"):
        return redirect("/login")
    else:
        login_check = True
    return login_check


def ordinal(n):
    if 11 <= n % 100 <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")

    return f"{n}{suffix}"