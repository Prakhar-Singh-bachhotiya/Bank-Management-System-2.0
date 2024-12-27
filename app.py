from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User
import random
import re
from datetime import *

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Routes

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']  # Example: '2004-06-07'
        city = request.form['city']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        acc_no = str(random.randint(1000000000, 9999999999))  # Generate a random 10-digit account number
        balance = request.form.get('balance', type=float, default=2000.0)
        address = request.form['address']
        # Password Validation
        if len(password) < 8 or not re.search(r'[A-Za-z0-9@#$%^&+=]', password):
            flash('Password must be at least 8 characters and contain a number or special character')
            return redirect(url_for('register'))

        if balance < 2000:
            flash("Minimum balance to open an account is 2000 ")

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))


        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()  # Adjust format as per your input
        except ValueError:
            return "Invalid date format. Please use YYYY-MM-DD.", 400
        
        # Create new user
        new_user = User(
            name=name,
            dob=dob,
            city=city,
            password=password,
            contact=contact,
            email=email,
            address=address,
            acc_no=acc_no,
            balance=balance
    )

        


        db.session.add(new_user)
        db.session.commit()

        flash('User registered successfully!')
        return redirect(url_for('dashboard'))
        
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    acc_no = request.form['acc_no']
    password = request.form['password']

    user = User.query.filter_by(acc_no=acc_no, password=password).first()

    if user:
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid account number or password')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch user data from the database
    user = User.query.filter_by(id=session['user_id']).first()
    if user:
        return render_template('dashboard.html', user=user)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.name = request.form['name']
        user.city = request.form['city']
        user.contact = request.form['contact']
        user.email = request.form['email']
        user.address = request.form['address']
        
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('dashboard'))

    return render_template('update_profile.html', user=user)

@app.route('/show_user')
def show_user():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    return render_template('show_user.html', user=user)

@app.route('/transaction', methods=['POST'])
def transaction():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    action = request.form['action']
    amount = float(request.form['amount'])

    if action == 'credit':
        user.balance += amount
        flash(f'Amount credited: {amount}')
    elif action == 'debit':
        if user.balance >= amount:
            user.balance -= amount
            flash(f'Amount debited: {amount}')
        else:
            flash('Insufficient balance')
    elif action == 'transfer':
        recipient_acc = request.form['recipient_acc']
        recipient = User.query.filter_by(acc_no=recipient_acc).first()
        if recipient:
            if user.balance >= amount:
                user.balance -= amount
                recipient.balance += amount
                flash(f'Amount transferred: {amount} to {recipient.name}')
            else:
                flash('Insufficient balance')
        else:
            flash('Recipient account not found')

    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/deactivate_account')
def deactivate_account():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    user.is_active = False
    db.session.commit()

    flash('Account deactivated successfully!')
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
