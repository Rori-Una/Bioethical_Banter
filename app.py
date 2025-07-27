import os
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
# import functions that allow password hashing and can check/confirm passwords

# initialise the application 
app = Flask(__name__)

# configure sessions such that it uses server-side management
app.config["SESSION_TYPE"] = "filesystem" 
# may also need to specify the directoy to store files in
app.config["SESSION_PERMANENT"] = False

# connect to the database
# "TODO"

# can start creating the routes 
# login route
@app.route("/login", methods=["GET", "POST"]) # define methods if needed
def login():
    # methods GET and POST
    if request.method == "POST":
        # collect form data, hash password, store in db 
        return render_template("prompt.html")
    else:
        return render_template("login.html")
    # "TODO"

# logout route
@app.route("/logout")
def logout():
    return redirect("index.html")
    # "TODO"

# index route
@app.route("/")
def index():
    return render_template("index.html")
    # "TODO"

# prompting route
@app.route("/prompt", methods=["GET", "POST"])
def prompting():
    if request.method == "POST":
        # first button allows user to save their response -> success message
        # second button triggers AI response [may not tie in with tis route's functionality??]
        return render_template("prompt.html")    
    else:             
        return render_template("prompt.html")
    # "TODO"

# management route 
@app.route("/management")
def management():
    # maybe saving functionality
    return render_template("planning.html")
    # "TODO"

if __name__ == "__main__":
    app.run(debug=True)