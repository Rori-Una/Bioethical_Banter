import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from passlib.hash import bcrypt
import sqlite3
import requests
import uuid

load_dotenv()

# initialise the application 
app = Flask(__name__)
app.secret_key = "super_secret_key_123"

# configure sessions such that it uses server-side management
app.config["SESSION_TYPE"] = "filesystem" 
app.config["SESSION_PERMANENT"] = False
app.config['SECRET_KEY'] = 'secret_key' # ideally something more secure

# initialise flask session
Session(app)

#AI integration stuff
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

def get_openai_response(user_message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    response = requests.post(OPENAI_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}"

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
    ai_response = None
    scenario = "You are a doctor facing an ethical dilemma: A patient refuses a life-saving treatment. What should you do?"
    paper_text = session.get("paper_text", "")
    questions_dict = session.get("questions_dict", {})
    selected_question_id = None
    user_answer = None
    conversation = None
    if request.method == "POST":
        selected_question_id = request.form.get("selected_question_id")
        user_answer = request.form.get("user_answer")
        selected_question = questions_dict.get(selected_question_id, "")
        if selected_question and user_answer:
            full_prompt = f"Scenario: {scenario}\n\nResearch Paper:\n{paper_text}\n\nQuestion: {selected_question}\nUser's answer: {user_answer}\n\nRespond as an expert, referring to the research paper and providing feedback on the user's answer."
            ai_response = get_openai_response(full_prompt)
            conversation = {
                "question": selected_question,
                "user_answer": user_answer,
                "ai_response": ai_response
            }
            # You can store 'conversation' in the database here for review/planning
    return render_template("prompt.html", ai_response=ai_response, scenario=scenario, questions_dict=questions_dict, selected_question_id=selected_question_id, user_answer=user_answer, conversation=conversation)
    # "TODO"

# management route 
@app.route("/management", methods=["GET", "POST"])
def management():
    scenario = None
    questions_dict = session.get("questions_dict", {})
    if request.method == "POST":
        paper_text = request.form.get("paper_text")
        if paper_text:
            session["paper_text"] = paper_text
        action = request.form.get("action")
        if action == "generate_questions" and paper_text:
            q_prompt = f"Read the following research paper and generate 5 thoughtful, open-ended ethical questions based on its content.\n\nResearch Paper:\n{paper_text}"
            questions_text = get_openai_response(q_prompt)
            questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
            # Store questions in a dict with unique IDs
            questions_dict = {str(uuid.uuid4()): q for q in questions}
            session["questions_dict"] = questions_dict
    return render_template("planning.html", questions_dict=questions_dict)

if __name__ == "__main__":
    app.run(debug=True)