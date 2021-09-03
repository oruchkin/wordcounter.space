import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, counter

from werkzeug.utils import secure_filename

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

    dictionary = db.execute("SELECT word, SUM(counter) FROM data GROUP BY WORD ORDER BY SUM(counter) DESC LIMIT 10")
    COUNT_words = db.execute("SELECT COUNT(DISTINCT word) FROM data")[0]["COUNT(DISTINCT word)"]
    COUNT_counter = db.execute("SELECT SUM(counter) FROM data")[0]["SUM(counter)"]

    return render_template("index.html", dictionary = dictionary, COUNT_words=COUNT_words, COUNT_counter=COUNT_counter)

# counter for string
@app.route("/query", methods=["GET", "POST"])
@login_required
def query():
    if request.method == "GET":
        return render_template("query.html")

    elif request.method == "POST":
        query_name = request.form.get("query_name")
        name_of_query = request.form.get("query_name")
        query_text = request.form.get("query_text").lower() #it is <class 'str'>

        user_id = session["user_id"]

        dictionary = counter(query_text)

        #adding constant time to sql
        my_datetime = datetime.datetime.now()
        date_to_sql = my_datetime.strftime("%d %b %y - %H:%M:%S")
        time = date_to_sql


        for word in dictionary:
            db.execute("INSERT INTO data (user_id, name_of_query, word, counter, time) VALUES (?, ?, ?, ?, ?)",
                   user_id, query_name, word, dictionary[word], date_to_sql )


        history = db.execute("SELECT word, SUM(counter) FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY word ORDER BY SUM(counter) DESC", name_of_query, time, user_id)
        COUNT_words = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["COUNT(word)"]
        COUNT_counter = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["SUM(counter)"]
        time_created = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["time"]

        return render_template("history_detail.html", history=history, name_of_query = name_of_query, COUNT_words=COUNT_words,  COUNT_counter = COUNT_counter, time_created=time_created)


# path for saving all uploads
app.config["TXT_UPLOADS"] = "/home/ubuntu/project/static/txt_uploads"
#checking if filename .txt name is actually .TXT format
app.config["ALLOWED_TXT_EXTENSIONS"] = ["TXT"]
def allowed_txt(filename):
    if not "." in filename:
        return False
    #spliting name by ".(dot)" and taking 1st element from the right
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in app.config["ALLOWED_TXT_EXTENSIONS"]:
        return True
    else:
        return False


# for .txt counter
@app.route("/query_txt", methods=["GET", "POST"])
@login_required
def query_txt():
    name_of_query = request.form.get("query_name")
    user_id = session["user_id"]

    if request.method == "GET":
        return render_template("query_txt.html")

    elif request.method == "POST":

        if request.files:
            query_txt = request.files["query_txt"]
            if query_txt.filename == "":
                return render_template("query_txt.html", message="Text must have a filename")

            elif not allowed_txt(query_txt.filename):
                return render_template("query_txt.html", message="That file extension is not allowed, ONLY .txt allowed")

            else:
                filename = secure_filename(query_txt.filename)  #lpnumb.txt

                #saving txt file, and giving "file_txt" its own name
                query_txt.save(os.path.join(app.config["TXT_UPLOADS"], filename))
                print("txt saved")
                # !COUNTER LOGIC START

                directory = "/home/ubuntu/project/static/txt_uploads"
                full_path = os.path.join(directory,filename)

                with open(full_path, "r") as file:
                    reader = file.read()
                    dictionary = {}
                    temp_word = ""

                    for n in reader:
                        i = n.lower()
                        if i.isalpha():
                            temp_word = temp_word + i

                        else:
                            if temp_word in dictionary:
                                dictionary[temp_word] += 1
                                temp_word = ""
                            else:
                                dictionary[temp_word] = int(1)
                                temp_word = ""

                    #keys to delete from data base (fake)
                    keys = ["", "s", "t", "a", "re", "m", "ll", "d", "o" ]

                    for i in keys:
                        if i in dictionary:
                            del dictionary[i]


                # !COUNTER LOGIC END
                #delete file
                os.remove(os.path.join(app.config['TXT_UPLOADS'], filename))
                print("txt deleted")


                my_datetime = datetime.datetime.now()
                date_to_sql = my_datetime.strftime("%d %b %y - %H:%M:%S")
                time = date_to_sql

                for word in dictionary:
                    db.execute("INSERT INTO data (user_id, name_of_query, word, counter, time) VALUES (?, ?, ?, ?, ?)",
                           user_id, name_of_query, word, dictionary[word], date_to_sql )


                #dictionary = db.execute("SELECT word, SUM(counter) FROM data WHERE name_of_query = ? AND time = ? GROUP BY word ORDER BY SUM(counter) DESC", name_of_query, date_to_sql)
                #return render_template("query_result.html", dictionary=dictionary, query_name=name_of_query)
                history = db.execute("SELECT word, SUM(counter) FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY word ORDER BY SUM(counter) DESC", name_of_query, time, user_id)
                COUNT_words = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["COUNT(word)"]
                COUNT_counter = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["SUM(counter)"]
                time_created = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["time"]

                return render_template("history_detail.html", history=history, name_of_query = name_of_query, COUNT_words=COUNT_words,  COUNT_counter = COUNT_counter, time_created=time_created)




            print(query_txt.filename)
            return redirect(request.url)

        return render_template("query_txt.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", message="MUST PROVIDE USERNAME")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", message="MUST PROVIDE PASSWORD")


        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", message="INVALID USERNAME AND/OR PASSWORD")


        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/login_forgot", methods=["GET", "POST"])
def login_forgot():
    return render_template("login_forgot.html")

@app.route("/global_words", methods=["GET"])
def global_words():


    dictionary = db.execute("SELECT word, SUM(counter) FROM data GROUP BY WORD ORDER BY SUM(counter) DESC")
    COUNT_words = db.execute("SELECT COUNT(DISTINCT word) FROM data")[0]["COUNT(DISTINCT word)"]
    COUNT_counter = db.execute("SELECT SUM(counter) FROM data")[0]["SUM(counter)"]

    return render_template("global_words.html", dictionary = dictionary, COUNT_words=COUNT_words, COUNT_counter=COUNT_counter)


@app.route("/global_words_personal", methods=["GET"])
@login_required
def global_words_persona():

    user_id = session["user_id"]

    dictionary = db.execute("SELECT word, SUM(counter) FROM data WHERE user_id = ? GROUP BY WORD ORDER BY SUM(counter) DESC", user_id)
    COUNT_words = db.execute("SELECT COUNT(DISTINCT word) FROM data WHERE user_id = ?", user_id)[0]["COUNT(DISTINCT word)"]
    COUNT_counter = db.execute("SELECT SUM(counter) FROM data WHERE user_id = ?", user_id)[0]["SUM(counter)"]


    return render_template("global_words_personal.html", dictionary = dictionary, COUNT_words=COUNT_words, COUNT_counter=COUNT_counter)


@app.route("/history", methods=["GET"])
@login_required
def history():

    user_id = session["user_id"]


    history = db.execute("SELECT name_of_query, time, COUNT(word), SUM(counter) FROM data WHERE user_id = ? GROUP BY time ORDER BY time DESC", user_id)

    return render_template("history.html", history = history)

@app.route("/history_detail", methods=["GET", "POST"])
@login_required
def history_detail():
    if request.method == "GET":
        return render_template("history_detail.html")

    elif request.method == "POST":
        user_id = session["user_id"]
        name_of_query = request.form.get("name_of_query")
        time = request.form.get("time")

        history = db.execute("SELECT word, SUM(counter) FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY word ORDER BY SUM(counter) DESC", name_of_query, time, user_id)

        #history_detail = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)
        #[{'time': '17 Jul 21 - 09:16:27', 'COUNT(word)': 2151, 'SUM(counter)': 11396}]
        COUNT_words = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["COUNT(word)"]
        COUNT_counter = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["SUM(counter)"]
        time_created = db.execute("SELECT time, COUNT(word), SUM(counter)  FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY time ORDER BY time DESC", name_of_query, time, user_id)[0]["time"]

        return render_template("history_detail.html", history=history, name_of_query = name_of_query, COUNT_words=COUNT_words,  COUNT_counter = COUNT_counter, time_created=time_created)


@app.route("/history_remove", methods=["GET"])
@login_required
def history_remove():

    user_id = session["user_id"]

    history = db.execute("SELECT name_of_query, time, COUNT(word), SUM(counter) FROM data WHERE user_id = ? GROUP BY time ORDER BY time DESC", user_id)

    return render_template("history_remove.html", history = history)



@app.route("/history_remove_logic", methods=["GET", "POST"])
@login_required
def history_remove_logic():
    if request.method == "GET":
        return render_template("history_remove.html")

    elif request.method == "POST":
        user_id = session["user_id"]
        name_of_query = request.form.get("name_of_query")
        time = request.form.get("time")

        #history = db.execute("SELECT word, SUM(counter) FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? GROUP BY word ORDER BY SUM(counter) DESC", name_of_query, time, user_id)

        history2 = db.execute("DELETE FROM data WHERE name_of_query = ? AND time = ? AND user_id = ? ", name_of_query, time, user_id)

        return redirect("/history")



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
            return render_template("register.html", message="YOU MUST PROVIDE USERNAME")

        elif not request.form.get("password"):
            return render_template("register.html", message="YOU MUST PROVIDE PASSWORD")

        elif not request.form.get("confirmation"):
            return render_template("register.html", message="YOU MUST PROVIDE PASSWORD AGAIN")


        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", message="PASSWORDS DO NOT MATCH")

        hash = generate_password_hash(request.form.get("password"))

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            return redirect("/login")
        except:
            return render_template("register.html", message="THIS USER NAME ALREADY EXIST")

            #return redirect("/login", message="registration successful")

            #return render_template("register.html", message="THIS USER NAME ALREADY EXIST")

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

