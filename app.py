from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from random import randint

from helpers import login_required, error, lookup

app = Flask(__name__)
app.run(debug=True)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    with sqlite3.connect("data.db") as conn:
        db = conn.cursor()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("username"):
            return error("must provide username")
        elif not request.form.get("password"):
            return error("must provide password")

        # Query database for username
        row = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"), )).fetchone()
        if row is None:
            return error("invalid username and/or password")
        if not check_password_hash(row[2], request.form.get("password")):
            return error("invalid username and/or password")

        session["user_id"] = hash

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()
    
    if request.method == "POST":
        if not request.form.get("username"):
            return error("must provide username", 400)

        elif not request.form.get("password"):
            return error("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return error("Passwords not the same", 400)

        with sqlite3.connect("data.db") as conn:
            db = conn.cursor()
            usernames = []
            for i in db.execute("SELECT username FROM users"):
                print(i)
                usernames.append(i[0])
            # raise TimeoutError
            # usernames = [i["username"] for i in db.execute("SELECT username FROM users")]
        if request.form.get("username") in usernames:
            return error("Username already in use", 400)

        username = request.form.get("username")
        email = request.form.get("email")
        phash = generate_password_hash(request.form.get("password"))

        with sqlite3.connect("data.db") as conn:
            db = conn.cursor()
            db.execute("INSERT INTO users (username, \"hash\", email) VALUES (?, ?, ?)", (username, phash, email))
        
        return render_template("login.html")
    else:
        return render_template("register.html")
    

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/game", methods=["POST"])
@login_required
def game():
    start = request.form.get("start")
    end = request.form.get("end")
    
    int_start = int(start[2:]) // 100 if not start == 'bce' else 9
    int_end = int(end[2:]) // 100 if not end == 'bce' else 9
    if int_start > int_end:
        return error("The start must be less than or equal to the end")
    
    if int_start == 9 and int_end != 9:
        return error("Cannot select BCE and CE at the same time")
    
    lst = ["bce", "ce1000", "ce1100", "ce1200", "ce1300", "ce1400", "ce1500", "ce1600", "ce1700", "ce1800", "ce1900", "ce2000", "ce2100"]
    while True:
        no = randint(int_start - 9, int_end - 9)
        with sqlite3.connect("data.db") as conn:
            db = conn.cursor()
            table = lst[no]
            rows = len(list(db.execute(f"SELECT * FROM {table}")))
            no = randint(1, rows)
            link, year = db.execute(f"SELECT link, year FROM {table} WHERE id = {no}").fetchone()

        session['year'] = year
        
        session['start_year'] = int_start * 100
        session['end_year'] = int_end  * 100

        info = lookup(link)

        print(link, info)
        if not info is None:
            break
    
    if int_start == 9 and int_end == 9:
        min, max = 0, 1000
        type = 'bce'
    elif int_start == 10 and int_end == 10:
        min, max = 0, 1000
        type = 'ce'
    else:
        min, max = int_start * 100 - 100, int_end * 100
        type = 'ce'

    session["range"] = max - min

    return render_template("play.html", info=info, min=min, max=max, type=type)


@app.route("/response", methods=["POST"])
@login_required
def response():
    year = int(request.form.get("year"))
    real_year = session.get("year")
    start_year = session.get("start_year")
    end_year = session.get("end_year")
    range_ = session.get("range")

    print(year, real_year)
    print(start_year, end_year)

    if '–' in real_year or '-' in real_year:
        start, end = real_year.split('–')
        if start > end:
            start, end = end, start
        print(start, end)
        start, end = int(start), int(end)

        if year >= start and year <= end:
            score = 100
        elif year < start:
            score = int((range_ - (start - year)) / range_ * 100) 
        else:
            score = int((range_ - (year - end)) / range_ * 100) 
    else:
        real_year = int(real_year)
        if year == real_year:
            score = 100
        elif year > real_year:
            score = int((range_ - (year - real_year)) / range_ * 100)
        else:
            score = int((range_ - (real_year - year)) / range_ * 100)
            
    dic = {900: "bce", 1000: "ce1000", 1100: "ce1100", 1200: "ce1200", 
            1300: "ce1300", 1400: "ce1400", 1500: "ce1500", 1600: "ce1600", 
            1700: "ce1700", 1800: "ce1800", 1900: "ce1900", 2000: "ce2000",
            2100: "ce2100"}
    
    return render_template("finished.html", score=score, guessed=year, correct=real_year)


@app.route("/again", methods=["POST"])
@login_required
def finished_response():
    return redirect("/")