# wordcounter.space
#### Video Demo:   [Youtube - wordcounter](https://www.youtube.com/watch?v=4fgXeRC0FEs).
#### Description:

The idea of the project is to allow any user to find the most frequently used
words according to their interests. It will be usefull for those who learn new
language and don't know which words to learn first

The program accepts any text as input (movie subtitles, music texts, books, articles)
And return to the user full statistics for this text, and sorted dictionary with most
frequent words in this text, referred  to the number how much times they appear in it

So user will now have the top frequent words, and he can start learn them, it
works in any language


## explanation of the code

There are two folders: Templates, static
a) Templates contains all of the pages of the site, and one of them is layout.html,
it is a "frame" for every other page
b) static contains all images, and stylesheet "style.css"
c)inside the static there is an empty folder "txt_uploads", all txt files are uploaded here
than they are immediately deleted after the logic is done with them

###### logic:
application.py:

1) @app.route("/", methods=["GET"]) ---> main page

2) @app.route("/query", methods=["GET", "POST"]) --- > query page
one of the main logic functions
it calls "counter" function which lies in helpers.py

3) app.config["TXT_UPLOADS"] --- > path where to save .txt files from user and
immediately delete them

4) function "def allowed_txt(filename)"  checks if the .txt file from user is
actually .txt and not .pdf or .jpg

5) @app.route("/query_txt", methods=["GET", "POST"])
it is the same as /query, but it takes from user .txt file, and inside of this path
there is a function, i had trouble to send file in helpers.py so i decieded to put function
inside of the path
this function takes .txt file, saving .txt, processing this file, and then deleting .txt file
in order to save hdd space

6) @app.route("/login", methods=["GET", "POST"]) --- > login page

7) @app.route("/login_forgot", methods=["GET", "POST"]) --- > login forgot page
it is a meme page, u cant actually change password, because we dont use e-mail
on registration

8) @app.route("/global_words", methods=["GET"]) --- > global words page

9) @app.route("/global_words_personal", methods=["GET"]) ---> same page as global
but your personal gloabl page

10) @app.route("/history_detail", methods=["GET", "POST"])
this page shows all details after processing input from user,
it also replaced page "query_result.html"
at 1st they was to same page, but with different time to appear
but than i moved them both in one, easier to configure them

11) @app.route("/history_remove", methods=["GET"])
this is the page where you delete your queries, i wanted to make it on same page
with "/history_detail" but i couldnt make two forms on one page, so i had to create
different page to it

12) @app.route("/history_remove_logic", methods=["GET", "POST"])
this page is doing logic to removing queries, it makes sql execution

13) @app.route("/logout") -
logout from your account

14) @app.route("/register", methods=["GET", "POST"])
registration, i used same registration and login functions as in finance pset

15) def errorhandler(e):
this is error handler, it calls apology funtcion, and it show a meme page, i like memes
try open page that doesnt exist
i also took it from finance pset

