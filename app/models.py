from app import db, app, login
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True,)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index = True, unique = True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    savings: so.Mapped['Savings'] = so.relationship(back_populates='user', uselist=False)
    income: so.Mapped['Income'] = so.relationship(back_populates='user', uselist=False)
    expenses: so.Mapped['Expense'] = so.relationship(back_populates='user')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password) # Encapsulate the password hashing
        return self.password_hash
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password) # True or False function, check between hashed and unhashed password

class Income(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    amount: so.Mapped[float] = so.mapped_column(sa.Float, index=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index = True)
    user: so.Mapped[User] = so.relationship(back_populates='income', uselist=False)
    __table_args__ = ( # Pass extra metadata to the table
        sa.CheckConstraint('amount >= 0', name='amount_positive'), # Ensure amount is non-negative, Alongside name for easier debugging
    )
    
class Expense(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    utilities: so.Mapped[float] = so.mapped_column(sa.Float)
    food: so.Mapped[float] = so.mapped_column(sa.Float)
    Miscellaneous: so.Mapped[float] = so.mapped_column(sa.Float)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index= True)
    user: so.Mapped[User] = so.relationship(back_populates='expenses')
    __table_args__ = (
        sa.CheckConstraint('utilities >= 0 AND food >= 0 AND Miscellaneous >= 0', name='expense_non_negative'),
    )
    
class Savings(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    goal: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0)
    saved: so.Mapped[float] = so.mapped_column(sa.Float, default=0.0) # Default is 0.0 in case no savings are logged yet
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True, unique=True) # Foreign key to link to User
    user: so.Mapped[User] = so.relationship(back_populates='savings', uselist=False)
    savings_logs: so.Mapped[list['SavingsLog']] = so.relationship(back_populates='savings', cascade='all, delete-orphan', uselist=True) # Cascade to delete logs if savings entry is deleted
    __table_args__ = (
        sa.CheckConstraint('goal >= 0 AND saved >= 0', name='savings_non_negative'),
    )

class SavingsLog(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    amount: so.Mapped[float] = so.mapped_column(sa.Float)
    timestamp: so.Mapped[datetime] = so.mapped_column(sa.DateTime, default=datetime.utcnow)    
    savings_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Savings.id), index=True)
    savings: so.Mapped["Savings"] = so.relationship("Savings", back_populates='savings_logs')
    __table_args__ = (
        sa.CheckConstraint('amount >= 0', name='savings_log_positive'),
    )
    
@login.user_loader # Decorator, loads a user from user ID, flask calls this whenever it needs data while a user is logged in a current session, login is my instance
def load_user(id): # We get the id to help the decorator keep track, we need the id
    return db.session.get(User, int(id))     
