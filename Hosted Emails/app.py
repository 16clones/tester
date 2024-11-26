from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Database model for whitelist
class Whitelist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)

# Ensure database is created
with app.app_context():
    db.create_all()

# Login page
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']

    # Check credentials and expiry
    user = Whitelist.query.filter_by(username=username, password=password).first()
    if user and user.expiry_date > datetime.now():
        session['username'] = username
        return redirect(url_for('python_page'))
    return "Invalid credentials or expired access!", 403

# Python page (after login)
@app.route('/python_page')
def python_page():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('python_page.html', username=session['username'])

# Admin panel for managing whitelist
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        duration = request.form['duration']
        expiry_date = datetime.now() + timedelta(days=int(duration))
        new_user = Whitelist(username=username, password=password, expiry_date=expiry_date)
        db.session.add(new_user)
        db.session.commit()
    users = Whitelist.query.all()
    return render_template('admin.html', users=users)

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
