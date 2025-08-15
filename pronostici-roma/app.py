import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from datetime import datetime
import pytz

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")

# DB persistente su Render
app.config["DATABASE"] = os.environ.get("DATABASE", "/data/db.sqlite3")

bcrypt = Bcrypt(app)

def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        is_admin INTEGER DEFAULT 0
                    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS matches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        home_team TEXT,
                        away_team TEXT,
                        match_time TEXT
                    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        match_id INTEGER,
                        score TEXT,
                        scorer TEXT,
                        UNIQUE(user_id, match_id)
                    )''')
    conn.commit()
    conn.close()

def add_user(username, password, is_admin=False):
    conn = get_db()
    cur = conn.cursor()
    hashed = bcrypt.generate_password_hash(password).decode("utf-8")
    try:
        cur.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                    (username, hashed, 1 if is_admin else 0))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

@app.route("/init")
def init():
    init_db()
    add_user("admin", "adminpass", is_admin=True)
    for i in range(1, 5):
        add_user(f"user{i}", f"pass{i}")
    return "Database inizializzato! Utenti: admin/adminpass e user1..4/pass1..4"

@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM matches")
    matches = cur.fetchall()
    conn.close()
    return render_template("index.html", matches=matches)

@app.route("/add_match", methods=["GET", "POST"])
def add_match():
    if "user_id" not in session or not session.get("is_admin"):
        return redirect(url_for("index"))
    if request.method == "POST":
        home_team = request.form["home_team"]
        away_team = request.form["away_team"]
        match_time = request.form["match_time"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO matches (home_team, away_team, match_time) VALUES (?, ?, ?)",
                    (home_team, away_team, match_time))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("add_match.html")

@app.route("/predict/<int:match_id>", methods=["GET", "POST"])
def predict(match_id):
    if "user_id" not in session:
        return redirect(url_for("index"))
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM matches WHERE id=?", (match_id,))
    match = cur.fetchone()
    if not match:
        return redirect(url_for("index"))
    rome_tz = pytz.timezone("Europe/Rome")
    match_time = datetime.strptime(match["match_time"], "%Y-%m-%d %H:%M")
    match_time = rome_tz.localize(match_time)
    now = datetime.now(rome_tz)
    if now >= match_time:
        flash("La partita è già iniziata!")
        return redirect(url_for("index"))
    if request.method == "POST":
        score = request.form["score"]
        scorer = request.form["scorer"]
        try:
            cur.execute("INSERT INTO predictions (user_id, match_id, score, scorer) VALUES (?, ?, ?, ?)",
                        (session["user_id"], match_id, score, scorer))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Hai già inserito un pronostico per questa partita!")
        conn.close()
        return redirect(url_for("index"))
    conn.close()
    return render_template("predict.html", match=match)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cur.fetchone()
        conn.close()
        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            return redirect(url_for("index"))
        else:
            flash("Credenziali errate!")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/predictions/<int:match_id>")
def view_predictions(match_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM matches WHERE id=?", (match_id,))
    match = cur.fetchone()
    if not match:
        return redirect(url_for("index"))
    rome_tz = pytz.timezone("Europe/Rome")
    match_time = datetime.strptime(match["match_time"], "%Y-%m-%d %H:%M")
    match_time = rome_tz.localize(match_time)
    now = datetime.now(rome_tz)
    if now < match_time:
        flash("I pronostici saranno visibili solo dopo la partita!")
        return redirect(url_for("index"))
    cur.execute("""SELECT u.username, p.score, p.scorer
                   FROM predictions p
                   JOIN users u ON p.user_id = u.id
                   WHERE p.match_id=?""", (match_id,))
    predictions = cur.fetchall()
    conn.close()
    return render_template("predictions.html", match=match, predictions=predictions)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
