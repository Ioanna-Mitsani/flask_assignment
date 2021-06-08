# Import here the classes needed from libraries or the whole libraries
from flask import Flask, render_template
# redirect, flash, request
from os import environ


app = Flask(__name__)


@app.get('/')
def home():
    return render_template("index.html")


@app.get('/login')
def login_page():
    return render_template("login.html")


if __name__ == '__main__':
    app.run(host="localhost", port=environ.get("PORT", 8080))
