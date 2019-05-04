from flask import Flask, send_from_directory, session, url_for, request, flash, redirect, render_template, g
import os
import sqlite3
import hashlib
import time
import secret

app = Flask(__name__)

app.secret_key = secret.key
DATABASE = 'craw.db'

# http://flask.pocoo.org/docs/1.0/patterns/sqlite3/
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # init the database if not exists
        init_db(db)
    return db

def init_db(db):
    """
    Creates db tables if not already set up
    """
    cur = db.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS crobdidates
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
        prez TEXT,
        vprz TEXT,
        slogan TEXT,    
        votes INTEGER)
    ''')

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def landing():
    return send_from_directory('static', 'index.html')

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
