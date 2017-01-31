from __future__ import print_function # In python 2.7
import sys, os, operator
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
import forms
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import User, Tickers, Transactions
from VotingApp import db, app, login_manager
from yahoo_finance import Share
from pytz import timezone
import requests

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
        # print(user, sys.stderr)
        # print(user.password, sys.stderr)
        if user is not None and user.check_password(password):
            login_user(user, False)
            return redirect(url_for('dashboard'))
        else:
            flash("Incorrect Email or Password")
            #return redirect(url_for('index'))
    elif request.method=='POST' and request.form['btn'] == 'Sign Up':
        if validateSignUp():
            user = User(email=setForm.setEmail.data,
                        firstName=setForm.firstName.data,
                        lastName=setForm.lastName.data,
                        password = setForm.setPassword.data)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        return render_template('index.html', form=form, setForm=setForm, login="login-hide", signup="signup-show", login_active="", signup_active="active")
    return render_template('index.html', form=form, setForm=setForm, login="login", signup="signup", login_active="active", signup_active="")

def validateSignUp():
    setForm = forms.SignUpForm()
    ok = True
    if User.query.filter_by(email=setForm.setEmail.data).first():
        flash("User with email already exists")
        ok = False
    if setForm.setPassword.data != setForm.setPassword2.data:
        flash("Passwords do NOT match")
        ok = False
    if (setForm.setEmail.data)[-10:] != "utexas.edu":
        flash("Must use utexas.edu email")
        ok = False
    if not setForm.setEmail.data or not setForm.firstName.data or not setForm.lastName.data or not setForm.setPassword.data:
        flash("All fields are required")
        ok = False
    return ok


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#TODO need to calculate and send todays, total gains
@app.route('/dashboard')
@login_required
def dashboard():
    """Getting Position on Leaderboard"""
    allUsers = User.query.all()
    returns = {}
    for student in allUsers:
        totalStocks = len(student.stocks)
        ret = 0
        activeStocks = student.stocks
        #Totals for each ticker
        totalGains = {}
        totalPercents = {}

        "Calculates returns on active positions"
        for stock in activeStocks:
            if(stock.short):
                ret += (stock.startingPrice - float(Share(stock.ticker).get_price()))/stock.startingPrice
            else:
                ret += (float(Share(stock.ticker).get_price()) - stock.startingPrice)/stock.startingPrice

        "Calculates returns on sold positions"
        userTransactions = Transactions.query.filter_by(user_id=student.id)
        totalStocks += userTransactions.count()
        for trans in userTransactions:
            transTicker = Tickers.query.filter_by(ticker=trans.ticker).first()
            if(transTicker.short):
                ret += (transTicker.startingPrice - trans.end_price)/transTicker.startingPrice
            else:
                ret += (trans.end_price - transTicker.startingPrice)/transTicker.startingPrice
        if totalStocks is not 0:
            returns[student.id] = ret/totalStocks
        else:
            returns[student.id] = 0
    "Sorts the dictionary by returns"
    ret_tups = sorted(returns.items(), key=operator.itemgetter(1), reverse=True)
    "Finds leadboard position"
    standing = 1
    for userid, ret in ret_tups:
        if userid is current_user.id:
            break
        standing += 1

    """Finished getting position"""
    prices = {}
    names = {}
    dates = {}
    changes = {}
    percentChanges = {}
    trends = {}
    for stock in current_user.stocks:
        prices[stock.ticker] = float("%.2f" % float(Share(stock.ticker).get_price()))
        names[stock.ticker] = get_name(stock.ticker)
        dates[stock.ticker] = get_datetime(stock.ticker)
        #TODO make need to take into shorts in get_gain and get_percent_change
        changes[stock.ticker] = get_gain(stock.ticker)
        percentChanges[stock.ticker] = get_percent_change(stock.ticker)
        if(stock.short):
            totalGains[stock.ticker] = (stock.startingPrice - float(Share(stock.ticker).get_price()))
            totalPercents[stock.ticker] = round(((stock.startingPrice - float(Share(stock.ticker).get_price()))/stock.startingPrice)*100, 2)
        else:
            totalGains[stock.ticker] = (float(Share(stock.ticker).get_price()) - stock.startingPrice)
            totalPercents[stock.ticker] = round(((float(Share(stock.ticker).get_price()) - stock.startingPrice)/stock.startingPrice)*100, 2)
    startingPrices = {}
    for stock in Tickers.query.all():
        startingPrices[stock.ticker] = stock.startingPrice
    exitedStocks = Transactions.query.filter_by(user_id=current_user.id)
    exitedStocksNames = {}
    exitedStockDates = {}
    #TODO Have to calculate totalGains and totalPercents for exited stocks
    for stock in exitedStocks:
        exitedStocksNames[stock.ticker] = get_name(stock.ticker)
        exitedStockDates[stock.ticker] = get_datetime(stock.ticker)
    return render_template('dashboard.html', stocks=current_user.stocks, prices=prices,
        names = names, totalReturn=returns[current_user.id], standing=standing, startingPrices=startingPrices,
        exitedStocks=exitedStocks, exitedStocksNames = exitedStocksNames, numExitedStocks = len(exitedStocksNames),
        numActiveStocks = len(current_user.stocks), firstName = current_user.firstName,
        lastName = current_user.lastName, dates = dates, exitedStockDates = exitedStockDates,
        changes = changes, percentChanges = percentChanges, totalGains = totalGains, totalPercents = totalPercents)

def get_name(ticker):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(ticker)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == ticker:
            return truncate(x['name'])

def truncate(name):

    if (len(name) > 17):
        words = name.split(" ")
        length = 0
        return_name = ""
        for x in words:
            if (len(x) + length + 1 < 17):
                return_name += x + " "
                length += len(x) + 1
            else:
                break
        return return_name

    return name

def get_datetime(ticker):
    eastern = timezone('US/Eastern')
    utc = timezone("UTC")
    dateString = Share(ticker).get_trade_datetime().split(" UTC")[0]
    d = datetime.strptime(dateString, "%Y-%m-%d %H:%M:%S")
    loc_d = utc.localize(d)
    est_d = loc_d.astimezone(eastern)
    fmt = "%b %d, %I:%M%p %Z"
    return est_d.strftime(fmt)

def get_gain(ticker):
    change = Share(ticker).get_change()
    #Needs to be replaced with a string to show error
    if change is None:
        return 0
    c = change.split("+")
    if (len(c) > 1):
        return float(c[1])
    return float(change)

def get_percent_change(ticker):
    percent = Share(ticker).get_percent_change()
    #Needs to be replaced with a string to show error
    if(percent is None):
        return 0
    string = percent.split("+")
    if len(string) <= 1:
        return percent
    return string[1]

#TODO take into account shorts in color of exited positions
@app.route('/exitPosition/<int:exitIndex>')
def exitPosition(exitIndex):
    #print(current_user.id)  #user_id
    #print(current_user.stocks[exitIndex-1].id)  #ticker_id
    """Deletes position from Active Positions"""
    user = User.query.filter_by(id=current_user.id).first()
    exitPosition = current_user.stocks[exitIndex-1]
    current_user.stocks.pop(exitIndex-1)
    db.session.commit()

    """Need to add to transactions table"""
    t = datetime.now()
    today = str(t.month) + "/" + str(t.day) + "/" + str(t.year)
    transaction = Transactions(user_id=current_user.id,
                ticker=exitPosition.ticker,
                date=today,
                end_price = float(Share(exitPosition.ticker).get_price()))
    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for('dashboard'))


@app.route('/loggedin')
def loggedin():
    return render_template('loggedin.html')
if __name__ == '__main__':
    app.run(debug=True)
