from flask import session, Blueprint, render_template, request, redirect
from tools import login_required, get_db_connection, ordinal
from datetime import datetime
import calendar
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

        columns = [desc[0] for desc in cur.description]
    except Exception as e:
        print(e)

    conn.commit()
    conn.close()

    return render_template("playerready/query.html", query=query, data=data, columns=columns)


@login_required
@playerready.route("/shifttable")
def shifttable():
    id = session.get("id")
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    now = datetime.now()
    print(now)
    if not month:
        month = now.month
    if not year:
        year = now.year
    
    days_json = {}
    num_days = calendar.monthrange(year, month)[1]
    for day in range(1, num_days + 1):
        date_obj = datetime(year, month, day)
        date_str = date_obj.strftime("%Y-%m-%d")
        day_str = f"{date_obj.strftime('%a')} {ordinal(day)}"

        conn, cur = get_db_connection()

        cur.execute(f"SELECT id, clock_in, clock_out, shift_type FROM playerready_{id} WHERE DATE(clock_in) = '{date_str}'")
        data = cur.fetchall()

        shifts = []
        for row in data:
            clock_in_dt = datetime.strptime(row["clock_in"], "%Y-%m-%d %H:%M:%S")
            clock_in_str = clock_in_dt.strftime("%H:%M")

            clock_out_dt = datetime.strptime(row["clock_out"], "%Y-%m-%d %H:%M:%S")
            clock_out_str = clock_out_dt.strftime("%H:%M")

            duration = clock_out_dt - clock_in_dt
            total_seconds = int(duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            duration_str = f"{hours:02}:{minutes:02}"

            shifts.append({"id": row["id"], "clock_in": clock_in_str, "clock_out": clock_out_str, "duration": duration_str})
    
        days_json[date_str] = {"day": day_str, "shifts": shifts}
    
    return render_template("playerready/shifttable.html", days=days_json)


@login_required
@playerready.route("/log-shift", methods=["POST"])
def log_shift():
    id = session.get("id")
    date = request.form.get("date")
    clock_in = request.form.get("clock-in")
    clock_out = request.form.get("clock-out")

    clock_in_dt = datetime.strptime(
    f"{date} {clock_in}",
    "%Y-%m-%d %H:%M"
    )

    clock_out_dt = datetime.strptime(
        f"{date} {clock_out}",
        "%Y-%m-%d %H:%M"
    )
    clock_in_sql = clock_in_dt.strftime("%Y-%m-%d %H:%M:%S")
    clock_out_sql = clock_out_dt.strftime("%Y-%m-%d %H:%M:%S")

    conn, cur = get_db_connection()

    cur.execute(f"INSERT INTO playerready_{id} (clock_in, clock_out, shift_type) VALUES ('{clock_in_sql}', '{clock_out_sql}', 'type_placeholder')")

    conn.commit()
    conn.close()

    return redirect("/playerready/shifttable")
