from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, counter

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database

db = SQL("sqlite:///wcounter.db")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/query", methods=["GET", "POST"])
@login_required
def query():
    if request.method == "GET":
        return render_template("query.html")
    elif request.method == "POST":
        query_name = request.form.get("query_name")
        query_text = request.form.get("query_text").lower() #it is <class 'str'>

        user_id = session["user_id"]

        dictionary = counter(query_text)

        print(user_id)
        print("dictionary")
        print(dictionary)
        print(type(dictionary))

        for word in dictionary:
            db.execute("INSERT INTO data (user_id, name_of_query, word, counter) VALUES (?, ?, ?, ?)",
                   user_id, query_name, word, dictionary[word] )

        #dictionary type (list) with ALOT of dictionaries inside
        #dictionary_test = db.execute("SELECT word, counter FROM data WHERE user_id = ?", user_id)

        dictionary_items = dictionary.items()
        sorted_items = sorted(dictionary.items(), key = lambda kv: kv[1], reverse=True)

        return render_template("query_result.html", dictionary=sorted_items, query_name=query_name)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/global_words", methods=["GET"])
def global_words():


    return render_template("global_words.html")


@app.route("/history")
@login_required
def history():
    return render_template("history.html")




@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if (request.method == "POST"):
        username = request.form.get("username")
        if not request.form.get("username"):
            return apology("must provide username")

        elif not request.form.get("password"):
            return apology("must provide password")

        elif not request.form.get("confirmation"):
            return apology("must provide password again")

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match")

        hash = generate_password_hash(request.form.get("password"))

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return redirect("/", message="registration successful")
        except:
            return apology("this user name already exist")

    elif (request.method == "GET"):
        return render_template("register.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

