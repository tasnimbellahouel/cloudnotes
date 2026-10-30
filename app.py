from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, hashlib, os
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cloudnotes-lab6-change-me')
DB = Path(__file__).with_name('website.db')

def db():
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row; return conn

def hash_password(password): return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = db(); conn.executescript('''
    CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL, content TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id));
    '''); conn.commit(); conn.close()

@app.route('/')
def home():
    if session.get('user_id'): return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username=request.form['username'].strip(); password=request.form['password']
        if len(username)<3 or len(password)<4:
            flash('Use at least 3 characters for the username and 4 for the password.'); return redirect(url_for('register'))
        conn=db()
        try:
            cur=conn.execute('INSERT INTO users(username,password) VALUES(?,?)',(username,hash_password(password))); conn.commit()
            session['user_id']=cur.lastrowid; session['username']=username; return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError: flash('That username is already taken.')
        finally: conn.close()
    return render_template('auth.html', mode='register')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form['username'].strip(); password=hash_password(request.form['password']); conn=db()
        user=conn.execute('SELECT * FROM users WHERE username=? AND password=?',(username,password)).fetchone(); conn.close()
        if user:
            session['user_id']=user['id']; session['username']=user['username']; return redirect(url_for('dashboard'))
        flash('Incorrect username or password.')
    return render_template('auth.html', mode='login')

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'): return redirect(url_for('login'))
    conn=db(); notes=conn.execute('SELECT * FROM notes WHERE user_id=? ORDER BY id DESC',(session['user_id'],)).fetchall(); conn.close()
    return render_template('dashboard.html', notes=notes)

@app.route('/notes', methods=['POST'])
def add_note():
    if not session.get('user_id'): return redirect(url_for('login'))
    title=request.form['title'].strip() or 'Untitled'; content=request.form['content'].strip()
    if content:
        conn=db(); conn.execute('INSERT INTO notes(user_id,title,content) VALUES(?,?,?)',(session['user_id'],title,content)); conn.commit(); conn.close()
    return redirect(url_for('dashboard'))

@app.route('/notes/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    if not session.get('user_id'): return redirect(url_for('login'))
    conn=db(); conn.execute('DELETE FROM notes WHERE id=? AND user_id=?',(note_id,session['user_id'])); conn.commit(); conn.close(); return redirect(url_for('dashboard'))

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('home'))

if __name__=='__main__':
    init_db(); app.run(host='0.0.0.0',port=8000)
