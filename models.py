from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), nullable=False)  # User's name
    dob = db.Column(db.Date, nullable=False)  # Date of birth
    city = db.Column(db.String(50), nullable=False)  # City
    password = db.Column(db.String(128), nullable=False)  # Password
    contact = db.Column(db.String(15), nullable=False, unique=True)  # Contact number
    email = db.Column(db.String(100), nullable=False, unique=True)  # Email address
    address = db.Column(db.String(200), nullable=False)  # Residential address
    acc_no = db.Column(db.String(10), unique=True, nullable=False)  # Unique account number
    balance = db.Column(db.Float, nullable=False, default=0.0)  # Account balance
    is_active = db.Column(db.Boolean, default=True)  # Account status: active/inactive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Account creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update timestamp

    # Relationships
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.name}, Account: {self.acc_no}>"

class Transaction(db.Model):
    __tablename__ = 'transaction'

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    type = db.Column(db.String(20), nullable=False)  # Transaction type: credit, debit, transfer
    amount = db.Column(db.Float, nullable=False)  # Amount involved in the transaction
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Transaction timestamp
    description = db.Column(db.String(200))  # Optional description of the transaction

    def __repr__(self):
        return f"<Transaction {self.type}, Amount: {self.amount}, User ID: {self.user_id}>"
