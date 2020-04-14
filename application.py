import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

user_id = -1
username= ""

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
    books = db.execute("SELECT * FROM books ORDER BY title ASC LIMIT 50").fetchall()

    #Get the data account
    user = request.form.get("user")
    password = request.form.get("password")
    page = 0

    for account in accounts:
        if ((account.email==user or account.username==user) and account.password==password):
            user_id=account.id
            username=account.username
            return render_template("home.html", username=username, books=books)

    return render_template("alert.html", message="User or password incorrect")

@app.route("/home/search", methods=["post"])
def search():

    title = request.form.get("title")
    titleUpper = "%"+title.title()+"%"
    titleLower = "%"+title.lower()+"%"
    author = request.form.get("author")
    authorUpper = "%"+author.title()+"%"
    year = request.form.get("year")
    isbn = request.form.get("isbn")

    if title != "":
        if author != "":
            if year != "":
                if isbn != "":
                    books = db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author AND year = :year AND isbn = :isbn LIMIT 50",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper, "year": year, "isbn": isbn}).fetchall()
                    return render_template("home.html", username=username, books=books, title=title, author=author, year=year, isbn=isbn)
                books = db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author AND year = :year LIMIT 50",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper, "year": year}).fetchall()
                return render_template("home.html", username=username, books=books, title=title, author=author, year=year)
            books = db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author LIMIT 50",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper}).fetchall()
            return render_template("home.html", username=username, books=books, title=title, author=author)
        books = db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower LIMIT 50)",{"titleUpper": titleUpper, "titleLower": titleLower}).fetchall()
        return render_template("home.html", username=username, books=books, title=title)


    if author != "":
        if year != "":
            if isbn != "":
                books = db.execute("SELECT * FROM books WHERE author LIKE :author AND year = :year AND isbn = :isbn LIMIT 50", {"author": authorUpper, "year": year, "isbn": isbn}).fetchall()
                return render_template("home.html", username=username, books=books, author=author, year=year, isbn=isbn)
            books = db.execute("SELECT * FROM books WHERE author LIKE :author AND year = :year LIMIT 50", {"author": authorUpper, "year": year}).fetchall()
            return render_template("home.html", username=username, books=books, author=author, year=year)
        books = db.execute("SELECT * FROM books WHERE author LIKE :author LIMIT 50", {"author": authorUpper}).fetchall()
        return render_template("home.html", username=username, books=books, author=author)

    if year != "":
        if isbn != "":
            books = db.execute("SELECT * FROM books WHERE year = :year AND isbn = :isbn LIMIT 50", {"year": year, "isbn": isbn}).fetchall()
            return render_template("home.html", username=username, books=books, year=year, isbn=isbn)
        books = db.execute("SELECT * FROM books WHERE year = :year LIMIT 50", {"year": year}).fetchall()
        return render_template("home.html", username=username, books=books, year=year)

    if isbn != "":
        books = db.execute("SELECT * FROM books WHERE isbn = :isbn LIMIT 50", {"isbn": isbn}).fetchall()
        return render_template("home.html", username=username, books=books, isbn=isbn)


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
