from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, points FROM users ORDER BY points DESC;")
    classifica = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", classifica=classifica)

@app.route("/pronostico", methods=["GET", "POST"])
def pronostico():
    if request.method == "POST":
        username = request.form["username"]
        partita_id = request.form["partita_id"]
        risultato = request.form["risultato"]
        marcatore = request.form["marcatore"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO pronostici (username, partita_id, risultato, marcatore) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;",
                    (username, partita_id, risultato, marcatore))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("index"))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, descrizione FROM partite;")
    partite = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("pronostico.html", partite=partite)

@app.route("/risultati", methods=["GET", "POST"])
def risultati():
    if request.method == "POST":
        partita_id = request.form["partita_id"]
        risultato = request.form["risultato"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE partite SET risultato_ufficiale = %s, conclusa = TRUE WHERE id = %s;",
                    (risultato, partita_id))
        # Calcolo punti
        cur.execute("SELECT username, risultato FROM pronostici WHERE partita_id = %s;", (partita_id,))
        pronostici = cur.fetchall()
        for username, ris in pronostici:
            if ris == risultato:
                cur.execute("UPDATE users SET points = points + 5 WHERE username = %s;", (username,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("risultati"))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, descrizione, risultato_ufficiale, conclusa FROM partite;")
    partite = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("risultati.html", partite=partite)

@app.route("/init")
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        points INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS partite (
        id SERIAL PRIMARY KEY,
        descrizione TEXT,
        risultato_ufficiale TEXT,
        conclusa BOOLEAN DEFAULT FALSE
    );
    CREATE TABLE IF NOT EXISTS pronostici (
        username TEXT REFERENCES users(username),
        partita_id INTEGER REFERENCES partite(id),
        risultato TEXT,
        marcatore TEXT,
        PRIMARY KEY(username, partita_id)
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
    return "Database inizializzato!"
