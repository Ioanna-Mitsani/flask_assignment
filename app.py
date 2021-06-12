from __future__ import print_function
# Import here the elements needed from libraries or whole libraries
from flask import Flask, render_template, request, session, redirect, flash, url_for, g
# redirect, flash, request abort
from os import environ
from pathlib import Path
import sqlite3


app = Flask(__name__)

# Secret key declaration to create browser session
app.secret_key = '5613a0e127ad32e2642d975d23932d7a786107ab79061b11'

DATABASE_PATH = Path(__file__).parent / 'data/flask_project.db'


def get_conn():
    if 'conn' not in g:     # hasattr(g, 'conn')
        app.logger.debug(f"» New Connection requested from endpoint '{request.endpoint}'")
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        g.conn = conn       # setattr(g, 'conn', conn)

    return g.conn


@app.before_request
def get_users():
    # Quick return if request comes from static asset
    if not request or request.endpoint == 'static':
        return

    if not hasattr(g, 'users'):
        cur = get_conn().cursor()
        users = cur.execute(
            '''
            SELECT [uid], [username], [password], [email], [f_name], [l_name], [address],
            [city], [country], [postal_code], [about] FROM [user]
            '''
        ).fetchall()

        setattr(g, 'users', users)


@app.teardown_request
def teardown_request(e):
    '''
    Close connection on request teardown
    '''
    if hasattr(g, 'conn'):
        app.logger.debug('» Teardown Request')
        app.logger.debug('» Connection closed')
        g.conn.close()


@app.teardown_appcontext
def close_connection(e):
    '''
    Close connection on appcontext teardown
    This will fire whether there was an exception or not
    '''
    if conn := g.pop('conn', None):
        app.logger.debug('» Teardown AppContext')
        app.logger.debug('» Connection closed')
        conn.close()


# Index page router
@app.get('/')
def homepage():
    return render_template("index.html")  # Renders index.html


@app.get('/dashboard')
def dashboard():
    return render_template("dashboard.html")


# Login form page 'GET' router
@app.get('/login')
def login_page():
    if session['username'] is None:
        return render_template("login.html")  # Renders login.html
    else:
        flash('You are already logged in!')
        return redirect(url_for('profile'))


# Login form 'POST' method handling
@app.post('/login')
def login():
    form_username = request.form.get('username')  # Registering the username input
    form_password = request.form.get('password')  # Registering the password input

    cur = get_conn().cursor()
    users = cur.execute(
            '''
            SELECT [uid], [username], [password], [email], [f_name], [l_name], [address],
            [city], [country], [postal_code], [about] FROM [user]
            '''
        ).fetchall()
    setattr(g, 'users', users)

    if form_username == users[0]['username'] and form_password == users[0]['password']:  # Credentials check with database
        session['username'] = form_username  # If credentials are valid, are registered to cookie
        session['password'] = form_password
        return redirect(url_for('dashboard'))
    else:
        return render_template('page-403.html'), 403  # Alternatively: abort(403)


@app.get('/profile')
def profile():
    # if session['username'] and session['password'] is not None:
    return render_template("profile.html")
    # else:
    # abort(403)


@app.get('/logout')
def logout():
    if session['username'] is not None and session['password'] is not None:
        session.pop('username')
        session.pop('password')
        return redirect(url_for('login_page'))
    else:
        flash('You are not logged in!')
        return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(host="localhost", port=environ.get("PORT", 5000))
