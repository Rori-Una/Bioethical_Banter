import os
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from passlib.hash import bcrypt
import sqlite3
# import functions that allow password hashing and can check/confirm passwords

# initialise the application 
app = Flask(__name__)

# configure sessions such that it uses server-side management
app.config["SESSION_TYPE"] = "filesystem" 
app.config["SESSION_PERMANENT"] = False
app.config['SECRET_KEY'] = 'secret_key' # ideally something more secure

# initialise flask session
Session(app)



# can start creating the routes 
# sign in route 
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        # retrieve form data
        username = request.form.get("username")
        if not username:
            message = "Please enter username"
            exit 
            return render_template("signin.html", message=message)
        password = request.form.get("password")
        if not password:
            message = "Please enter password"
            exit 
            return render_template("signin.html", message=message)
        confirmation = request.form.get("confirmation")
        if not confirmation:
            message = "Please enter password confrimation"
            exit 
            return render_template("signin.html", message=message)
        # check passwords they match
        if password != confirmation:
            failure = "Passwords do not match. Try again"
            exit 
            return render_template("signin.html", message=failure)
        # hash the password and store in users
        hash = bcrypt.hash(password)
        # "TODO" insert data into db     
        conn = sqlite3.connect('biobanter.db', check_same_thread=False)
        db = conn.cursor()
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, hash)) 
        conn.commit()
        conn.close()
        # set user's session
        # session["name"] = username
        return render_template("prompt.html")
    else:
        return render_template("signin.html")
# login route
@app.route("/login", methods=["GET", "POST"]) # define methods if needed
def login():
    # methods GET and POST
    if request.method == "POST":
        # collect form data, hash password, store in db 
        username = request.form.get("username")
        password = request.form.get("password")
        # verify password
        conn = sqlite3.connect('biobanter.db', check_same_thread=False)
        db = conn.cursor()
        # dbUser = db.execute("SELECT username FROM users WHERE username = (?)", username)
        # verify the password matches the name
        dbHash = db.execute("SELECT hash FROM users WHERE username = (?)", [username]) 
        dbHashVal = db.fetchall()
        hash = dbHashVal[0][0]
        passVer = bcrypt.verify(password, hash)
        if passVer == True:
            return render_template("prompt.html")
        else:
            failure = "invalid password"
            return render_template("login.html", message=failure)
        # set user's session
        session["name"] = username
        return render_template("login.html", message=hash)
    else:
        return render_template("login.html")
    # "TODO"

# logout route
@app.route("/logout")
def logout():
    session["name"] = None
    return redirect("/")
    # "TODO"

# index route
@app.route("/")
def index():
    return render_template("index.html")
    # "TODO"

# prompting route
@app.route("/prompt", methods=["GET", "POST"])
def prompting():
    # check if user is in session
              
    return render_template("prompt.html")
    # "TODO"

# management route 
@app.route("/management")
def management():
    # check if user is in session
     
    # maybe saving functionality
    return render_template("planning.html")
    # "TODO"

if __name__ == "__main__":
    app.run(debug=True)