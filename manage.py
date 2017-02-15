from VotingApp.mainApp import app, db
from VotingApp.models import User, Tickers
from flask.ext.script import Manager, prompt_bool
import requests

manager = Manager(app)

@manager.command
def initdb():
    db.create_all()
    apple = Tickers(ticker="AAPL", startingPrice=89.8, short=True)
    signet = Tickers(ticker="SIG", startingPrice=90)
    google = Tickers(ticker="GOOG", startingPrice=400)
    aal = Tickers(ticker="AAL", startingPrice=40.00)
    tesla = Tickers(ticker="TSLA", startingPrice=50.00)
    db.session.add(User(firstName="Dilan", lastName="Hira",email="dilan@utexas.edu", password="test", stocks=[apple, signet]))
    db.session.add(User(firstName="Arnav", lastName="Jain",email="arnav@utexas.edu", password="test", stocks=[google, apple, signet, aal, tesla]))
    #db.session.add(apple)
    db.session.commit()
    print 'Initialized the database'

@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Dropped the database'

if __name__ == '__main__':
    manager.run()
