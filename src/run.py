import matplotlib as mpl
mpl.use('Agg')
import numpy as np
from matplotlib import pyplot as pyp
from flask import Flask, send_from_directory, session, url_for, request, flash, redirect, render_template, g
import os
import sqlite3
import hashlib
import time
import secret
from crob import profile as crob_profile
from crobnish import profile as crobnish_profile
from vote import Vote

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
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM crobdidates WHERE writein = FALSE')
        crobdidates = []
        for row in cur.fetchall():
            print(row)
            crobdidates.append(Vote(row[0], row[1], row[2], row[3], row[4], row[5]))
        
        return render_template('vote.html', crobdidates = crobdidates)
    return render_template('home.html')

@app.route('/results', methods=['GET', 'POST'])
def count_vote():
    if 'candidate' in request.form and request.form['candidate'] != "-1":
        print('standard candidates selected')
        print(str(request.form['candidate']))
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            c = int(request.form['candidate'])
            cur.execute('SELECT * FROM crobdidates WHERE id = ?', (c,))
            result = cur.fetchone()
            print(str(result))
            newvotes = int(result[5]) + 1
            cur.execute('UPDATE crobdidates SET votes = ? WHERE id = ?', (newvotes, int(request.form['candidate'])))
            db.commit()
            
    elif 'writein' in request.form and request.form['writein']:
        print('writein candidate selected!')
        print(request.form['writein'])
        with app.app_context():
            db = get_db()
            cur = db.cursor()
            cur.execute('SELECT * FROM crobdidates WHERE prez = ?', (request.form['writein'],))
            result = cur.fetchone()
            if not result:
                cur.execute('INSERT INTO crobdidates (prez, vprz, slogan, writein, votes) VALUES (?, ?, ?, ?, ?)', (request.form['writein'], "", "", True, 1))
            else:
                cur.execute('UPDATE crobdidates SET votes = ? WHERE id = ?', (int(result[5]) + 1, int(result[0])))
            db.commit()
    data = []
    with app.app_context():
        db = get_db()
        cur = db.cursor()
        cur.execute('SELECT * FROM crobdidates ORDER BY votes DESC')
        for row in cur.fetchall():
            data.append(Vote(row[0], row[1], row[2], row[3], row[4], row[5]))
    # print(str(data))
    graph_file = render_graph(data)
    return render_template('results.html', graph_file=graph_file, data = data)

def render_graph(data):
    fig = pyp.figure()
    pyp.pie([int(v.votes) for v in data], labels=[v.prez for v in data])
    pyp.axis('equal')
    filename = 'static/images/graphs/generated' + str(time.time()) + '.png'
    pyp.savefig(filename, bbox_inches='tight')
    return filename

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
