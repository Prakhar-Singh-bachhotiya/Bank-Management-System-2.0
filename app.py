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

from flask import render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import re
from werkzeug.security import generate_password_hash

# Assuming the 'User' model is already defined in your app
# from yourapp.models import User
from flask import render_template, request, redirect, url_for, flash
import random
import re
from datetime import datetime
from werkzeug.security import generate_password_hash

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name']
        dob = request.form['dob']
        city = request.form['city']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        balance = request.form.get('balance', type=float, default=2000.0)
        address = request.form['address']

        # Generate a random account number
        acc_no = str(random.randint(1000000000, 9999999999))

        # Password validation
        if len(password) < 8 or not re.search(r'[A-Za-z0-9@#$%^&+=]', password):
            flash('Password must be at least 8 characters and contain a number or special character')
            return redirect(url_for('register'))

        if balance < 2000:
            flash("Minimum balance to open an account is 2000")
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('register'))

        # Date validation
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return redirect(url_for('register'))

        

        # Create new user instance
        new_user = User(
            name=name,
            dob=dob,
            city=city,
            contact=contact,
            email=email,
            password=password,
            address=address,
            acc_no=acc_no,
            balance=balance
        )

        try:
            # Add user to the database
            db.session.add(new_user)
            db.session.commit()
            flash(f'User registered successfully! Your account number is: {acc_no}')
            return render_template('dashboard.html')  # Redirect to dashboard after successful registration
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {e}')
            return redirect(url_for('register'))

    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    login_id = request.form['Login_ID']
    password = request.form['password']

    user = User.query.filter(((User.acc_no == login_id) | (User.contact == login_id)), User.password==password).first()

    if user:
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid account number or password')
        return redirect(url_for('home'))

@app.route('/dashboard',methods=['GET', 'POST'])
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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Fetch the logged-in user's data
    user = User.query.filter_by(id=session['user_id']).first()
    
    if request.method == 'POST':
        # Update user profile
        try:
            user.name = request.form['name']
            user.email = request.form['email']
            user.contact = request.form['contact']
            user.dob = request.form['dob']
            user.city = request.form['city']
            user.address = request.form['address']
            user.dob = request.form['dob']
            user.dob = datetime.strptime(user.dob, '%Y-%m-%d').date()
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')

    return render_template('profile.html', user=user)

@app.route('/show_user')
def show_user():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    return render_template('show_user.html', user=user)

@app.route('/toggle_active/<int:user_id>', methods=['POST'])
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active  # Toggle active status
    db.session.commit()
    status = "activated" if user.is_active else "deactivated"
    flash(f"Account has been {status} successfully.", "success")
    return redirect(url_for('update_profile'))

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

@app.route('/deposit_money', methods=['GET', 'POST'])
def deposit_money():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        deposit_method = request.form['deposit_method']

        # Get current user (assuming logged in user)
        current_user = User.query.first()  # Change to actual logged-in user

        current_user.balance += amount
        db.session.commit()

        flash(f'Deposited ₹{amount} via {deposit_method}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('deposit_money.html')

@app.route('/transfer_funds', methods=['GET', 'POST'])
def transfer_funds():
    if request.method == 'POST':
        recipient_account = request.form['account_number']
        amount = float(request.form['amount'])
        transfer_note = request.form.get('transfer_note', '')

        # Get current user (assuming logged in user)
        current_user = User.query.first()  # This should be changed to get the logged-in user

        recipient = User.query.filter_by(acc_no=recipient_account).first()
        if recipient:
            if current_user.balance >= amount:
                current_user.balance -= amount
                recipient.balance += amount
                db.session.commit()
                flash('Funds transferred successfully!', 'success')
            else:
                flash('Insufficient balance!', 'danger')
        else:
            flash('Recipient account not found!', 'danger')

        return redirect(url_for('dashboard'))

    return render_template('transfer_funds.html')

@app.route('/withdraw_money', methods=['GET', 'POST'])
def withdraw_money():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        withdraw_method = request.form['withdraw_method']

        # Get current user (assuming logged in user)
        current_user = User.query.first()  # Change to actual logged-in user

        if current_user.balance >= amount:
            current_user.balance -= amount
            db.session.commit()

            flash(f'₹{amount} withdrawn via {withdraw_method}!', 'success')
        else:
            flash('Insufficient balance for withdrawal!', 'danger')

        return redirect(url_for('dashboard'))

    return render_template('withdraw_money.html')

from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # If not logged in, redirect to login

    user = User.query.get(session['user_id'])  # Get the current logged-in user
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Check if the current password is correct (no hashing)
        if user.password == current_password:  # Directly compare plain text passwords
            if new_password == confirm_password:  # Check if new passwords match
                if len(new_password) >= 8 and re.search(r'[A-Za-z0-9@#$%^&+=]', new_password):  # Password validation
                    # Update the password directly
                    user.password = new_password
                    db.session.commit()
                    flash('Password updated successfully!', 'success')  # Flash success message
                    return redirect(url_for('dashboard'))  # Redirect to dashboard after success
                else:
                    flash('New password must be at least 8 characters and contain a number or special character', 'danger')
            else:
                flash('New passwords do not match', 'danger')
        else:
            flash('Current password is incorrect', 'danger')

    return render_template('change_password.html', user=user)


if __name__ == "__main__":
    app.run(debug=True)
