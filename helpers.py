import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import get_string


def counter(query_text):
    reader = query_text
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

    return dictionary



def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


