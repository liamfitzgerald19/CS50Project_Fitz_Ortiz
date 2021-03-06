from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__, template_folder='templates')

# Ensure responses aren't cached
if app.config["DEBUG"]:
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
db = SQL("sqlite:///walkly.db")


@app.route("/history")
@login_required
def history():
    return render_template("history.html")

@app.route("/ineedhelp", methods=["GET", "POST"])
@login_required
def ineedhelp():
    return render_template("ineedhelp.html")

@app.route("/command")
@login_required
def command():
    personals = db.execute("SELECT Name, Age, Allergies, Favorite_Snack FROM Pets")
    rows = db.execute("SELECT Pets.Name, users.username as UsersName, Pets.Directions, Pets.Points FROM Pets JOIN users WHERE Pets.id = users.id")
    return render_template("command.html", personals=personals, rows=rows)



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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/command")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
    if request.method == "GET":
        return render_template("register.html")
    else:
        users_password_hash = generate_password_hash(request.form.get("password"))
        if not request.form.get("username"):
            return apology("Missing username!", 400)
        elif not request.form.get("password"):
            return apology("Missing password!", 400)
        elif not request.form.get("confirmation"):
            return apology("Missing confirmation password!", 400)
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("Incorrect. Please try again!", 400)
        elif not len(rows) == 0:
            return apology("Username already exists!", 400)
        else:
            db.execute("INSERT INTO users (username, hash) VALUES(:username, :users_password_hash)", username = request.form.get("username"), users_password_hash = users_password_hash)
            rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
            session["user_id"] = rows[0]["id"]
            if not rows:
                return apology("Username already exists!", 400)
            return redirect("/command")


def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

@app.route("/addpet", methods=["GET", "POST"])
@login_required
def addpet():
    if request.method == "POST":
        pet_data = db.execute("SELECT * FROM Pets WHERE id = :id",
                          id=session["user_id"])
        db.execute("INSERT INTO Pets (id, Name, Age, Allergies, Favorite_Snack, Additional_Notes, Animal) VALUES (:id, :name, :age, :allergies, :snack, :notes, :Animal)",
                    id=session["user_id"],
                    name=request.form.get("Name"),
                    age=request.form.get("Age"),
                    allergies=request.form.get("Allergies"),
                    snack=request.form.get("Favorite_Snack"),
                    notes=request.form.get("Additional_Notes"),
                    Animal=request.form.get("Animal"))
        return redirect("/addpet")
    else:

        return render_template("addpet.html")

@app.route("/deletepet", methods=["GET", "POST"])
@login_required
def delpet():
    if request.method == "POST":
        db.execute("DELETE FROM Pets WHERE Name = :name", name=request.form.get("Name"))
        return redirect("/deletepet")
    else:
        return render_template("deletepet.html")

