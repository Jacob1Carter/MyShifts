from flask import Flask
from mainroutes import main
from playerready import playerready
from tools import get_db_connection
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.before_request
def construct_db():
    # check that db exists
    if not os.path.exists("data/database.db"):
        with open("data/database.db", "w"):
            pass
    conn, cur = get_db_connection()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, name TEXT NOT NULL, password_md5 TEXT NOT NULL, datetime TEXT DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.commit()
    conn.close()


app.register_blueprint(main)
app.register_blueprint(playerready, url_prefix="/playerready")


if __name__ == "__main__":
    app.run()