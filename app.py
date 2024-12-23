import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, checknumber

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    cash = db.execute("SELECT cash, username FROM users WHERE id = ?", session["user_id"])
    total_cash = cash[0]["cash"]
    username = cash[0]["username"]

    symbol = db. execute("SELECT symbol, quantity FROM property WHERE person_id = ?", session["user_id"])

    return render_template("index.html", total=total_cash, username=username, rows= symbol, cant=len(symbol))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        #validation of symbols
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("must provide symbol and quantity", 403)
        elif not lookup(request.form.get("symbol")):
            return apology("This symbol does not exist")
        elif checknumber(request.form.get("shares"))== False:
            return apology("Is not a number")
        elif (int(request.form.get("shares"))<=0):
            return apology("must provide a valid quantity")
        donecash = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"], )
        usercash = donecash[0]["cash"]
        diccionario = lookup(request.form.get("symbol"))
        price = diccionario["price"]
        shares = int(request.form.get("shares"))
        total_value = price*shares
        if total_value > usercash:
            return apology ("Insuficient cash")
        else:
            cash = usercash - total_value
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash , session["user_id"])
            value = db.execute("SELECT quantity FROM property WHERE person_id = ? AND symbol = ?", session["user_id"], request.form.get("symbol"))
            if len(value) == 0:
                db.execute("INSERT INTO property (person_id, quantity, symbol) VALUES (?,?,?);", session["user_id"], int(request.form.get("shares")), request.form.get("symbol"))
            else:
                quantitydb = value[0]["quantity"]
                totalquantity = quantitydb + shares
                db.execute("UPDATE property SET quantity = ? WHERE person_id = ? AND symbol = ?", totalquantity, session["user_id"], request.form.get("symbol"))
        return render_template("bought.html", price=price)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # Ensure symbol is on there
        if not request.form.get("symbol"):
            return apology("Not avaiable", 400)
        elif not lookup(request.form.get("symbol")):
            return apology("This symbol does not exist", 400)
        dictionary = lookup(request.form.get("symbol"))
        price =  dictionary["price"]
        return render_template("quoted.html", price= price)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # COnfirmation
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # verification of password
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology ("must provide the same", 400)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 0 :
            return apology("repetitive username", 400)

        #hasheo
        hash = generate_password_hash(request.form.get("password"), method='pbkdf2', salt_length=16)

        #save on the database
        added = db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?);", request.form.get("username"), hash)
        if not added:
            return apology ("Was not posible your registration", 400)
        # Redirect user to home page
        return redirect("/")
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        #validation of symbols
        if not request.form.get("symbol"):
            return apology("must provide symbol", 403)
        elif check(request.form.get("shares"))==False:
            return apology("You don't have stock")
        name = db.execute("SELECT symbol FROM property WHERE person_id=?", session["user_id"], )
        print(name)
    else:
        return render_template("sell.html")
