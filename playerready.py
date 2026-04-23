from flask import session, Blueprint, render_template, request, redirect
from tools import login_required, get_db_connection
import os


playerready = Blueprint("playerready", __name__)


@login_required
@playerready.route("/setup", methods=["POST"])
def setup():
    wage = request.form.get("wage")
    conn, cur = get_db_connection()
    id = session.get("id")
    cur.execute(f"UPDATE users SET playerready = {float(wage)} WHERE id = {id}")
    cur.execute(
        f"CREATE TABLE IF NOT EXISTS playerready_{id} (id INTEGER PRIMARY KEY AUTOINCREMENT, clock_in TEXT UNIQUE NOT NULL, clock_out TEXT NOT NULL, shift_type TEXT NOT NULL, pay_rate REAL DEFAULT 100)"
    )
    conn.commit()
    conn.close()
    return redirect("/playerready")


@login_required
@playerready.route("/")
def landing():
    return render_template("playerready/landing.html")


@login_required
@playerready.route("/query", methods=["GET", "POST"])
def query():
    id = session.get("id")
    query = f"SELECT * FROM playerready_{id} ORDER BY id"
    if request.method == "POST":
        query = request.form.get("query")
    
    conn, cur = get_db_connection()

    try:
        cur.execute(query)
        data = cur.fetchall()
    except Exception as e:
        print(e)

    conn.commit()
    conn.close()

    return render_template("playerready/query.html", query=query, data=data)
