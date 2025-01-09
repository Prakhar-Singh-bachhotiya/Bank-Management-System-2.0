from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db
import random
import re
from datetime import *
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


migrate=Migrate(app,db)
from models import User, Transaction

db.init_app(app)

# Routes

@app.route('/')
def home():
    return render_template('login.html')






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
    current_user = User.query.filter_by(id=session['user_id']).first()
    if current_user:
        transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.timestamp.desc()).limit(5).all()

        return render_template('dashboard.html', user=current_user, transactions=transactions)
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
        current_user = User.query.filter_by(id=session['user_id']).first()  

        current_user.balance += amount
        transaction=Transaction(
                    user_id=current_user.id,
                    type='credit',
                    amount=amount,
                    description=f'Money Deposited via {deposit_method}'
                
        )
        db.session.add(transaction)
        db.session.commit()

        flash(f'Deposited ₹{amount} via {deposit_method}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('deposit_money.html')

@app.route('/transfer_funds', methods=['GET', 'POST'])
def transfer_funds():
    # Get all users excluding the current user
    current_user = User.query.filter_by(id=session['user_id']).first()  # Replace this with the logic to get the logged-in user
    all_recipients = User.query.filter(User.id != current_user.id).all()

    if request.method == 'POST':
        recipient_id = request.form['recipient_id']
        amount = float(request.form['amount'])
        transfer_note = request.form.get('transfer_note', '')

        recipient = User.query.filter_by(id=recipient_id).first()
        if recipient:
            if current_user.balance >= amount:
                # Perform the fund transfer
                current_user.balance -= amount
                recipient.balance += amount

                # Create transaction records
                sender_transaction = Transaction(
                    user_id=current_user.id,
                    type='debit',
                    amount=amount,
                    description=f'Transfered to {recipient.name}: {transfer_note}'
                )
                recipient_transaction = Transaction(
                    user_id=recipient.id,
                    type='credit',
                    amount=amount,
                    description=f'Received from {current_user.name}: {transfer_note}'
                )

                # Add transactions to the database
                db.session.add(sender_transaction)
                db.session.add(recipient_transaction)

                db.session.commit()
                flash('Funds transferred successfully!', 'success')
            else:
                flash('Insufficient balance!', 'danger')
        else:
            flash('Recipient account not found!', 'danger')

        return redirect(url_for('dashboard'))

    return render_template('transfer_funds.html', recipients=all_recipients)

@app.route('/withdraw_money', methods=['GET', 'POST'])
def withdraw_money():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        withdraw_method = request.form['withdraw_method']

        # Get current user (assuming logged in user)
        current_user = User.query.filter_by(id=session['user_id']).first()

        if current_user.balance >= amount:
            current_user.balance -= amount
            transaction = Transaction(
                user_id=current_user.id,
                type='debit',
                amount=amount,
                description=f'Withdrawal via {withdraw_method}'
            )
            db.session.add(transaction)
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

from flask import render_template, request, session
from models import User, Transaction  # Import your models

@app.route('/view_transactions', methods=['GET'])
def view_transactions():
    # Get the current user
    current_user = User.query.filter_by(id=session['user_id']).first()

    # Get filter parameters
    transaction_type = request.args.get('type')
    date_filter = request.args.get('date')

    # Query transactions
    query = Transaction.query.filter_by(user_id=current_user.id)
    if transaction_type:
        query = query.filter_by(type=transaction_type)
    if date_filter:
        query = query.filter(Transaction.timestamp.like(f'{date_filter}%'))

    # Pagination (10 transactions per page)
    page = request.args.get('page', 1, type=int)
    transactions = query.order_by(Transaction.timestamp.desc()).paginate(page=page, per_page=10)

    return render_template('transactions.html', transactions=transactions)

@app.route('/delete_account/<int:user_id>', methods=['POST'])
def delete_account(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.balance > 0:
        flash('Your account balance must be ₹0 to delete the account.', 'danger')
        return redirect(url_for('update_profile'))
    
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted successfully.', 'success')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
