from flask import Flask, send_from_directory, session, url_for, request, flash, redirect, render_template, g
import os
import sqlite3
import hashlib
import time
import secret
from crob import profile as crob_profile
from crobnish import profile as crobnish_profile


app = Flask(__name__)

app.secret_key = secret.key
DATABASE = 'crobbiparti.db'

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
        writein BOOL,
        votes INTEGER)
    ''')
    # add two primary candidates
    cur.execute('SELECT id FROM crobdidates WHERE prez = ? AND vprz = ?', (crob_profile['prez'], crob_profile['vprz']))
    result = cur.fetchone()
    if result is None:
        # database is new and primary candidates do not exist yet
        print('creating crob + zetlen')
        cur.execute('INSERT INTO crobdidates (prez, vprz, slogan, writein, votes) VALUES (?, ?, ?, ?, ?)', (crob_profile['prez'], crob_profile['vprz'], crob_profile['slogan'], False, 0))
        db.commit()
    cur.execute('SELECT id FROM crobdidates WHERE prez = ? AND vprz = ?', (crobnish_profile['prez'], crobnish_profile['vprz']))
    result = cur.fetchone()
    if result is None:
        # database is new and primary candidates do not exist yet
        print('creating crobnish + zetlen')
        cur.execute('INSERT INTO crobdidates (prez, vprz, slogan, writein, votes) VALUES (?, ?, ?, ?, ?)', (crobnish_profile['prez'], crobnish_profile['vprz'], crobnish_profile['slogan'], False, 0))
        db.commit()
    return

@app.teardown_appcontext
def close_db_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def landing():
    # testing for testiboi purposes
    # db = get_db()
    return render_template('home.html')

@app.route('/vote', methods=['POST'])
def vote():
    return render_template('vote.html')

@app.route('/count_vote', methods=['GET', 'POST'])
def count_vote():
    # TODO: get form data (request.form)
    # TODO: commit new data to db
    # TODO: call routine to generate graph, return filename
    return render_template('results.html', graph_file="")

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
