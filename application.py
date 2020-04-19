import os, requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

class User:
    def __init__(self, id, username):
        self.id = id
        self.username = username

user = User(-1,"")

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
def index():
    return render_template("login.html")

@app.route("/home", methods=["post"])
def login():
    books = db.execute("SELECT * FROM books ORDER BY title ASC LIMIT 50").fetchall()
    accounts = db.execute("SELECT * FROM accounts").fetchall()

    #Get the data account
    user_form = request.form.get("user")
    password_form = request.form.get("password")

    for account in accounts:
        if ((account.email==user_form or account.username==user_form) and account.password==password_form):
            user.id = account.id
            user.username = account.username
            return render_template("home.html", username=user.username, books=books)

    return render_template("alert.html", message="User or password incorrect")

@app.route("/home/search", methods=["post"])
def search():

    title = request.form.get("title")
    titleUpper = "%"+title.title()+"%"
    titleLower = "%"+title.lower()+"%"
    author = request.form.get("author")
    authorUpper = "%"+author.title()+"%"
    try:
        year = int(request.form.get("year"))
    except:
        year = 0
    isbn = request.form.get("isbn")

    if title != "":
        if author != "":
            if year != 0:
                if isbn != "":
                    if db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author AND year = :year AND isbn = :isbn",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper, "year": year, "isbn": isbn}).rowcount == 0:
                        return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
                    books = db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author AND year = :year AND isbn = :isbn LIMIT 50",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper, "year": year, "isbn": isbn}).fetchall()
                    return render_template("home.html", username=user.username, books=books, title=title, author=author, year=year, isbn=isbn)
                if db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author AND year = :year",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper, "year": year}).rowcount == 0:
                    return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
                books = db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author AND year = :year LIMIT 50",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper, "year": year}).fetchall()
                return render_template("home.html", username=user.username, books=books, title=title, author=author, year=year)
            if db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper}).rowcount == 0:
                return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
            books = db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower) AND author LIKE :author LIMIT 50",{"titleUpper": titleUpper, "titleLower": titleLower, "author": authorUpper}).fetchall()
            return render_template("home.html", username=user.username, books=books, title=title, author=author)
        if db.execute("SELECT * FROM books WHERE (title LIKE :titleUpper OR title LIKE :titleLower)",{"titleUpper": titleUpper, "titleLower": titleLower}).rowcount == 0:
            return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
        books = db.execute("SELECT * FROM books WHERE title LIKE :titleUpper OR title LIKE :titleLower LIMIT 50",{"titleUpper": titleUpper, "titleLower": titleLower}).fetchall()
        return render_template("home.html", username=user.username, books=books, title=title)

    if author != "":
        if year != 0:
            if isbn != "":
                if db.execute("SELECT * FROM books WHERE author LIKE :author AND year = :year AND isbn = :isbn", {"author": authorUpper, "year": year, "isbn": isbn}).rowcount == 0:
                    return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
                books = db.execute("SELECT * FROM books WHERE author LIKE :author AND year = :year AND isbn = :isbn LIMIT 50", {"author": authorUpper, "year": year, "isbn": isbn}).fetchall()
                return render_template("home.html", username=user.username, books=books, author=author, year=year, isbn=isbn)
            if db.execute("SELECT * FROM books WHERE author LIKE :author AND year = :year", {"author": authorUpper, "year": year}).rowcount == 0:
                return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
            books = db.execute("SELECT * FROM books WHERE author LIKE :author AND year = :year LIMIT 50", {"author": authorUpper, "year": year}).fetchall()
            return render_template("home.html", username=user.username, books=books, author=author, year=year)
        if db.execute("SELECT * FROM books WHERE author LIKE :author", {"author": authorUpper}).rowcount == 0:
            return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
        books = db.execute("SELECT * FROM books WHERE author LIKE :author LIMIT 50", {"author": authorUpper}).fetchall()
        return render_template("home.html", username=user.username, books=books, author=author)

    if year != 0:
        if isbn != "":
            if db.execute("SELECT * FROM books WHERE year = :year AND isbn = :isbn LIMIT 50", {"year": year, "isbn": isbn}).rowcount == 0:
                return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
            books = db.execute("SELECT * FROM books WHERE year = :year AND isbn = :isbn LIMIT 50", {"year": year, "isbn": isbn}).fetchall()
            return render_template("home.html", username=user.username, books=books, year=year, isbn=isbn)
        if db.execute("SELECT * FROM books WHERE year = :year LIMIT 50", {"year": year}).rowcount == 0:
            return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
        books = db.execute("SELECT * FROM books WHERE year = :year LIMIT 50", {"year": year}).fetchall()
        return render_template("home.html", username=user.username, books=books, year=year)

    if isbn != "":
        if db.execute("SELECT * FROM books WHERE isbn = :isbn LIMIT 50", {"isbn": isbn}).rowcount == 0:
            return render_template("alert.html", code="No book found :(", message="Plese, chech your search!")
        books = db.execute("SELECT * FROM books WHERE isbn = :isbn LIMIT 50", {"isbn": isbn}).fetchall()
        return render_template("home.html", username=user.username, books=books, isbn=isbn)

    if (title == "" and author == "" and year == 0 and isbn == ""):
        books = db.execute("SELECT * FROM books ORDER BY title ASC LIMIT 50").fetchall()
        return render_template("home.html", username=user.username, books=books)
    return render_template("alert.html",code = "Not Found", message = "Sorry there isn't any book :(")

@app.route("/book/<isbn>", methods=["GET", "POST"])
def book(isbn):
    #Reviews for this book
    reviews = db.execute("SELECT username, valoration, score FROM accounts JOIN reviews ON reviews.user_id = accounts.id WHERE isbn = :isbn", {"isbn": isbn})

    #Edit a valoration
    if (request.method == "POST" and (db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id", {"isbn": isbn, "user_id": user.id}).rowcount==1)):
        valoration = request.form.get("valoration")
        score = request.form.get("score")
        db.execute("UPDATE reviews SET valoration = :valoration, score = :score WHERE isbn = :isbn AND user_id = :user_id",{"valoration": valoration, "score": score,"isbn": isbn, "user_id": user.id})
        db.commit()

    #Create a valoration
    if (request.method == "POST" and (db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id", {"isbn": isbn, "user_id": user.id}).rowcount==0)):
        valoration = request.form.get("valoration")
        score = request.form.get("score")
        db.execute("INSERT INTO reviews (user_id, isbn, valoration, score) VALUES (:user_id, :isbn, :valoration, :score)", {"user_id":user.id, "isbn":isbn, "valoration": valoration, "score":score})
        db.commit()

    #Valorations BooksLand
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchone()
    if db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn":isbn}).rowcount > 0:
        bookslanReview = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn":isbn}).rowcount
        BookslandScore = db.execute("SELECT AVG(score) FROM reviews WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
        BookslandScore = str(BookslandScore[0])
        BookslandScore = BookslandScore[0]+BookslandScore[1]+BookslandScore[2]+BookslandScore[3]
    else:
        bookslanReview = 0
        BookslandScore = "-"

    #Valorations Goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "10r5mLk1uqbZHS6RUJqRQ", "isbns": isbn})
    res = res.json()
    goodreadReview = res["books"][0]["work_ratings_count"]
    goodreadScore = res["books"][0]["average_rating"]

    #Check if you have written a review yet
    if db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id", {"isbn": isbn, "user_id": user.id}).rowcount>0:
        userReview = db.execute("SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id", {"isbn": isbn, "user_id": user.id}).fetchone()
        return render_template("book.html", reviews=reviews, username=user.username, book=book, isbn=isbn, bookslanReview=bookslanReview, BookslandScore=BookslandScore, goodreadReview=goodreadReview, goodreadScore=goodreadScore, valoration_user=userReview.valoration, score_user=userReview.score)

    return render_template("book.html", reviews=reviews, username=user.username, book=book, isbn=isbn, bookslanReview=bookslanReview, BookslandScore=BookslandScore, goodreadReview=goodreadReview, goodreadScore=goodreadScore, valoration_user="", score_user="")

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
