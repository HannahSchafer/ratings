"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template, redirect, request,
                    flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/registration-form')
def show_registration():
    """Show the registration form"""

    return render_template("reg_form.html")


@app.route('/process-registration', methods=['POST'])
def process_registration():
    """Check the given email against the database"""

    given_email = request.form.get("email")
    given_password = request.form.get("password")
    print given_email

    existing_user = User.query.filter(User.email==given_email).first()

    if existing_user:
        flash("Great job! You already exist in our universe! Please log in!")
        return redirect("/login-form")

    else:
        new_user = User(email=given_email, password=given_password)
        user_id = new_user.user_id

        # We need to add to the session or it won't ever be stored
        db.session.add(new_user)

        # Once we're done, we should commit our work
        db.session.commit()
        flash("user id = %s" % new_user.user_id)
        flash("Great job! Welcome to our universe! Get ready to pass judgement.")
        session["user_id"] = user_id

        return redirect("/")


@app.route('/login-form')
def show_login():
    """Display login form."""

    return render_template("login_form.html")

@app.route('/login-validation')
def check_login():
    """Compares login info to database info."""

    email = request.args.get("email")
    password = request.args.get("password")

    valid_user = User.query.filter((User.email==email) & (User.password==
                                    password)).first()

    if valid_user:
        # add state of logged-in-ness to session
        session["user_id"] = valid_user.user_id
        # redirect to '/'
        flash("You are logged in now.")
        return redirect("/")
    else:
        flash("Username and password do not match. please try again")
        return redirect("/login-form")

@app.route("/logged-out")
def log_out():
    """Log out."""

    del session["user_id"] 
    flash("you are so logged out.")
    return redirect("/")


@app.route("/<user_id>-details")
def show_user_details(user_id):
    """Shows each user's details when specific user clicked on.
    """
    user_object = User.query.get(user_id)
    ratings = user_object.ratings
    movies = [rating.movie.title for rating in ratings]

    return render_template("user_details.html", age=user_object.age, zipcode=user_object.zipcode, movies=movies)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
