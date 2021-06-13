# Import here the elements needed from libraries or whole libraries
from flask import Flask, render_template, request, session, redirect, flash, url_for, g
# redirect, flash, request abort
from os import environ
from pathlib import Path
import sqlite3


app = Flask(__name__)

# Secret key declaration to create browser session
app.secret_key = environ.get('SECRET_KEY', 'random1234')

DATABASE_PATH = Path(__file__).parent / environ.get('DB_PATH', 'data/flask_project.db')


# Function that initializes the connection to Database
def get_conn():
    if not hasattr(g, 'conn'):
        app.logger.debug(f"New Connection requested from endpoint '{request.endpoint}'")
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        setattr(g, 'conn', conn)
    return g.conn


# Function that closes connection to database on appcontext teardown
@app.teardown_appcontext
def close_connection(e):
    if conn := g.pop('conn', None):
        app.logger.debug('» Teardown AppContext')
        app.logger.debug('» Connection closed')
        conn.close()


# Index page router
@app.get('/')
def homepage():
    return render_template("index.html")  # Renders index.html


# Dashboard router
@app.get('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template("dashboard.html")
    else:
        return render_template('page-401.html')


# Login form page 'GET' router handling function
@app.get('/login')
def login_page():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html')  # Renders login.html


# Login form 'POST' method handling
@app.post('/login')
def login():
    form_username = request.form.get('username')  # Registering the username input
    form_password = request.form.get('password')  # Registering the password input

    cur = get_conn().cursor()                     # Creating cursor for executing query on db
    user = cur.execute(
            '''
            SELECT [uid], [username], [password]
            FROM [user]
            WHERE [username] = :username AND [password] = :password
            ''',
            {'username': form_username, 'password': form_password}
        ).fetchone()
    setattr(g, 'user', user)

    if form_username == user['username'] and form_password == user['password']:  # Credentials check with the ones in database
        session['username'] = user['username']  # If credentials are valid, are registered to session
        session['password'] = user['password']
        return redirect(url_for('dashboard'))   # Then user gets to dashboard page
    else:
        flash('Please enter the correct credentials!')  # If credentials are wrong a message flashes and gets redirected to /login
        return redirect(url_for('login_page'))


# Profile router handling function
@app.route('/profile/<username>')   # Profile needs router param to be accessed
def profile(username):
    if 'username' in session:       # If user is logged in, we fetch all his data from db
        cur = get_conn().cursor()
        user = cur.execute(
            '''
            SELECT *
            FROM [user]
            WHERE [username] = :username
            ''',
            {'username': username}
        ).fetchone()

        if user is None:
            return render_template('page-404.html')   # If query results are empty the profile doesn't exist --> 404

        if username == session['username']:
            return render_template('profile.html', user=user)
        else:
            return render_template('page-401.html')

    else:
        flash('You need to login first!')   # If user is not logged in he gets redirected to login page
        return redirect(url_for('login_page'))


# Logout handling
@app.get('/logout')
def logout():
    if 'username' in session:   # If 'username' is registered in session, then user is logged in
        session.pop('username')     # We remove the registered values
        session.pop('password')
        return redirect(url_for('login_page'))  # And we redirect to login
    else:
        flash('You are not logged in!')     # If someone tries to logout without being logged in, message appears
        return redirect(url_for('login_page'))           # and gets redirected to login page


@app.errorhandler(404)
def error404(e):
    return render_template('page-404.html'), 404


@app.errorhandler(401)
def error401(e):
    return render_template('page-401.html'), 401


@app.errorhandler(500)
def error500(e):
    return render_template('page-500.html'), 500


if __name__ == '__main__':
    app.run(host="localhost", port=environ.get("PORT", 5000))
