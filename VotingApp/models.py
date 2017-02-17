from datetime import datetime
from VotingApp import db
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import json
import requests
from flask_security import RoleMixin

ticker_identifier = db.Table('student_identifier',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('ticker_id', db.Integer, db.ForeignKey('tickers.id'))
)
#required for Flask-Security, could be useful later for admin screen
roles_users = db.Table('roles_users',
		db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
		db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

def get_json(ticker):
    url = "https://www.google.com/finance/info?q=NSE:{}".format(ticker)

    result = requests.get(url).text.split("// ")

    if len(result) > 1:
        rjson = json.loads(result[1])
    else:
        rjson = json.loads(result)

    return rjson

def get_price(ticker):
    rjson = get_json(ticker)
    return float(rjson[0][u'l'])

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(80))
    lastName = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String)
    active = db.Column(db.Boolean)
    stocks = db.relationship('Tickers', secondary=ticker_identifier, backref='user')
    transactions = db.relationship('Transactions', backref='user')
    #required for Flask-Security
    roles =  db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    @property
    def ret(self):
        ret = 0
        totalStocks = 0

        for stock in self.stocks:
            price = float(get_price(stock.ticker))

            if (stock.short):
                ret += (stock.startingPrice - price)/stock.startingPrice
            else:
                ret += (price - stock.startingPrice)/stock.startingPrice

            totalStocks += 1

        for trans in self.transactions:
            transTicker = Tickers.query.filter_by(ticker=trans.ticker).first()

            if(transTicker.short):
                ret += (transTicker.startingPrice - trans.end_price)/transTicker.startingPrice
            else:    
                ret += (trans.end_price - transTicker.startingPrice)/transTicker.startingPrice

            totalStocks += 1

        if totalStocks != 0:
            return ret/totalStocks
        else:
            return 0

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()

    def __repr__(self):
        return "<User '{}'>".format(self.email)


class Tickers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(5), unique=True)
    startingPrice = db.Column(db.Float)
    short = db.Column(db.Boolean)
    transactions = db.relationship('Transactions', backref='tickers')
    #user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return "<Ticker '{}'>".format(self.ticker)

class Transactions(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticker = db.Column(db.Integer, db.ForeignKey('tickers.id'), nullable=False)
    date = db.Column(db.String)
    end_price = db.Column(db.Integer)

# Flask Security
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(80))
