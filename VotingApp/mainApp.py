from __future__ import print_function # In python 2.7
import sys, os
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
import forms
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import User, Tickers
from VotingApp import db, app, login_manager

basedir = os.path.abspath(os.path.dirname(__file__))

# app = Flask(__name__)
# app.config['SECRET_KEY'] = '~t\x86\xc9\x1ew\x8bOcX\x85O\xb6\xa2\x11kL\xd1\xce\x7f\x14<y\x9e'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'usit.db')
# db = SQLAlchemy(app)

@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def index():
    form = forms.LoginForm()
    setForm = forms.SignUpForm()
    if request.method=='POST' and request.form['btn'] == 'log in':
        email = form.email.data
        password = form.password.data
        user = User.get_by_email(email)
        print(user, sys.stderr)
        print(user.password, sys.stderr)
        if user is not None and user.check_password(password):
            login_user(user, False)
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect Email or Password")
            #return redirect(url_for('index'))
    elif request.method=='POST' and request.form['btn'] == 'Sign Up':
        user = User(email=setForm.setEmail.data,
                    firstName=setForm.firstName.data,
                    lastName=setForm.lastName.data,
                    password = setForm.setPassword.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('index.html', form=form, setForm=setForm)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user, sys.stderr)
    return render_template('dashboard.html', stocks=current_user.stocks)


@app.route('/loggedin')
def loggedin():
    return render_template('loggedin.html')
if __name__ == '__main__':
    app.run(debug=True)
