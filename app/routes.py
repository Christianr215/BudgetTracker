from app import app, db
from flask import render_template, flash, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegisterForm, EditProfileForm, ExpenseForm, SavingsLogForm
from app.models import User, Income, Expense, Savings, SavingsLog
from urllib.parse import urlsplit
import sqlalchemy as sa
from sqlalchemy import Function as func
import json
from datetime import datetime

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    savings_form = SavingsLogForm()
    expense_form = ExpenseForm()

    if savings_form.validate_on_submit() and 'amount' in request.form:
        amount = savings_form.amount.data
        savings_entry = Savings.query.filter_by(user_id=current_user.id).first()
        if not savings_entry:
            savings_entry = Savings(user_id=current_user.id, goal=0, saved=0)
            db.session.add(savings_entry)
            db.session.commit()

        # Add new savings log
        new_log = SavingsLog(amount=amount, savings_id=savings_entry.id)
        savings_entry.saved += amount
        db.session.add(new_log)
        db.session.commit()
        flash("Savings added!", "success")
        if savings_entry.saved >= current_user.savings.goal:
            flash("Congratulations! You've reached your savings goal!", "success")
        return redirect(url_for('index'))

    if expense_form.validate_on_submit():
        utilities = expense_form.utilities.data
        food = expense_form.food.data
        misc = expense_form.Miscellaneous.data

        new_expense = Expense(
            user_id=current_user.id,
            utilities=utilities,
            food=food,
            Miscellaneous=misc
        )
        db.session.add(new_expense)
        db.session.commit()
        flash("Expense added!", "danger")
        return redirect(url_for('index'))

    # line chart
    savings_entry = Savings.query.filter_by(user_id=current_user.id).first()

    if savings_entry and savings_entry.savings_logs:
        logs = sorted(savings_entry.savings_logs, key=lambda x: x.timestamp)
        savings_labels = [log.timestamp.strftime("%b %d") for log in logs]
        savings_data = [log.amount for log in logs]
    
    else:
        savings_labels = ["No Data"]
        savings_data = [0]

    # pie chart
    expenses = Expense.query.filter_by(user_id=current_user.id).all()
    expense_labels = ['Utilities', 'Food', 'Miscellaneous']
    expense_totals = [0, 0, 0]
    for e in expenses:
        expense_totals[0] += e.utilities
        expense_totals[1] += e.food
        expense_totals[2] += e.Miscellaneous
        
    income_entry = Income.query.filter_by(user_id=current_user.id).first()
    income = income_entry.amount if income_entry else 0

    # Calculate remaining
    total_spent = sum(expense_totals)
    remaining = income - total_spent if income > total_spent else 0

    expense_totals.append(remaining)

    return render_template(
        'index.html', 
        title='Dashboard',
        savings_form=savings_form,
        expense_form=expense_form,
        savings_labels=json.dumps(savings_labels),
        savings_data=json.dumps(savings_data),
        expense_labels=json.dumps(expense_labels),
        expense_data=json.dumps(expense_totals)
    )
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('Login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next') # Request gives access to HTTP title commands, args is the part after ? and then im getting whatever is the value for the next 
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index') # First we check if there was a next value,if not, then netloc is the part of a website name where its the .com, essentially protecthing against false leading websites
        return redirect(next_page) # Url split breaks up url into 3 parts, netloc is .com part
        # If it passed the if statement part, it can go on. otherwise it becomes index
    return render_template('login.html', title='Sign in', form=form)
@app.route('/Logout')
def Logout():
    logout_user()
    return redirect(url_for('login'))
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        income = Income(amount=form.income.data, user = user) # Set it to user object
        savings = Savings(goal=form.goal.data, saved=form.savings.data, user=user)
        db.session.add(user)
        db.session.add(income)
        db.session.add(savings)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.income.amount = form.income.data
        current_user.savings.goal = form.goal.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('profile'))      
    elif request.method == 'GET':
        form.income.data = current_user.income.amount # Preload the form with previous entered data
        form.goal.data = current_user.savings.goal
    return render_template('edit_profile.html', title='Edit Profile', form=form)
@app.route('/log_expense', methods=['GET', 'POST'])
@login_required
def log_expense():
    form = ExpenseForm()
    if form.validate_on_submit():
        utilities = Expense(utilities=form.utilities.data, user = current_user)
        food = Expense(food=form.food.data, user = current_user)
        Miscellaneous = Expense(Miscellaneous=form.Miscellaneous.data, user = current_user)
        db.session.add(utilities)
        db.session.add(food)
        db.session.add(Miscellaneous)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('index.html', title='Dashboard', form=form)
@app.route('/log_savings', methods=['GET', 'POST'])
@login_required
def log_savings():
    form = SavingsLogForm()
    if form.validate_on_submit():
        savings = Savings.query.filter_by(user_id=current_user.id).first()
        if not savings:
            savings = Savings(user = current_user, goal=0.0, saved=0.0)
            db.session.add(savings)
            db.session.commit()
        log = SavingsLog(amount=form.amount.data, savings = savings) # Link log to savings entry
        db.session.add(log)
        savings.saved += form.amount.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('index.html', title='Dashboard', form=form)
@app.route('/profile')
@login_required
def profile():
    if current_user.savings:
        goal = current_user.savings.goal
    else:
        goal = 0.0
    if current_user.income:
        income = current_user.income.amount
    else:
        income = 0.0
    return render_template('user.html', title='Profile', user=current_user, goal = goal, income=income)
@app.route('/about')
def about():
    return render_template('about.html', title='About Me')
    