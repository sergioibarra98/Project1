import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def login():
    return render_template("login.html")

@app.route("/home", methods=["post"])
def home():
    accounts = db.execute("SELECT * FROM accounts").fetchall()

    #Get the data account
    user = request.form.get("user")
    password = request.form.get("password")

    for account in accounts:
        if ((account.email==user or account.username==user) and account.password==password):
            return render_template("home.html",username=account.username)

    return render_template("alert.html", message="User or password incorrect")


@app.route("/register")
def register():
    return render_template("signup.html")

@app.route("/register/status", methods=["POST"])
def checkRegister():
    accounts = db.execute("SELECT * FROM accounts").fetchall()

    #Get the new data account
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")

    for account in accounts:
        if (email == ""):
            return render_template("alert.html", code="Something has gone wrong", message="The email can't be empty"), 400
        if (username == ""):
            return render_template("alert.html", code="Something has gone wrong", message="The username can't be empty"), 400
        if (password == ""):
            return render_template("alert.html", code="Something has gone wrong", message="The password can't be empty"), 400
        if (account.email == email) :
            return render_template("alert.html", code="Something has gone wrong", message="This email is already registered"), 400
        if (account.username == username):
            return render_template("alert.html", code="Something has gone wrong", message="This username is already used"), 400

    db.execute("INSERT INTO accounts (email, username, password) VALUES (:email,:username, :password)",{"email":email, "username":username, "password":password})
    db.commit()
    return render_template("alert.html",code="Success", message="Everything OK, please go back and log in :D"), 201
