from VotingApp.mainApp import app, db
from VotingApp.models import User, Tickers
from flask.ext.script import Manager, prompt_bool

manager = Manager(app)

@manager.command
def initdb():
    db.create_all()
    db.session.add(User(firstName="LeBron", lastName="James",email="dilan@webitup.com", password="test", stocks=[Tickers(ticker='ATVI')]))
    apple = Tickers(ticker="AAPL")
    db.session.add(User(firstName="Dilan", lastName="Hira",email="dilan@utexas.edu", password="test", stocks=[apple]))
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
