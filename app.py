# Import here the elements needed from libraries or whole libraries
from flask import Flask, render_template, request, session, redirect, flash, url_for, g
# redirect, flash, request abort
from os import environ
from pathlib import Path
import sqlite3


app = Flask(__name__)

# Secret key declaration to create browser session
app.secret_key = environ.get('SECRET_KEY', 'random1234')

DATABASE_PATH = Path(__file__).parent / environ.get("DB_PATH", 'data/flask_project.db')


# Function that initializes the connection to Database
def get_conn():
    if not hasattr(g, 'conn'):
        app.logger.debug(f"New Connection requested from endpoint '{request.endpoint}'")
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        setattr(g, 'conn', conn)
    return g.conn


# Function executed before every request
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


# Function that destroys connection to database
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


# Dashboard router
@app.get('/dashboard')
def dashboard():
    if session['username']:
        return render_template("dashboard.html")
    else:
        return render_template('page-403.html')


# Login form page 'GET' router
@app.get('/login')
def login_page():
    if session:
        return redirect(url_for('dashboard'))

    return render_template('login.html')  # Renders login.html


# Login form 'POST' method handling
@app.post('/login')
def login():
    form_username = request.form.get('username')  # Registering the username input
    form_password = request.form.get('password')  # Registering the password input

    cur = get_conn().cursor()
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
        session['username'] = user['username']  # If credentials are valid, are registered to session obj
        session['password'] = user['password']
        return redirect(url_for('dashboard'))
    else:
        flash('Please enter the correct credentials!')
        return redirect(url_for('login_page'))


@app.route('/profile/<username>')
def profile(username):
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
        return render_template('page-404.html')

    return render_template('profile.html', user=user)


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
