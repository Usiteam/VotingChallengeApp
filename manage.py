from VotingApp.mainApp import app, db, update_ret, add_stock, update_score, create_stock_info
from VotingApp.models import User, Tickers, Role, Transactions
from flask_script import Manager, prompt_bool
from openpyxl import load_workbook, Workbook
import requests

manager = Manager(app)

# @manager.command
# def initdb():
#     db.create_all()
#     apple = Tickers(ticker="AAPL", startingPrice=89.8, short=True)
#     signet = Tickers(ticker="SIG", startingPrice=90)
#     google = Tickers(ticker="GOOG", startingPrice=400)
#     aal = Tickers(ticker="AAL", startingPrice=40.00)
#     tesla = Tickers(ticker="TSLA", startingPrice=50.00)
#     admin = Role(name="Admin", description="Gets to look at all the rankings.")
#     db.session.add(User(firstName="Dilan", lastName="Hira",email="dilan@utexas.edu", password="test", stocks=[apple, signet]))
#     db.session.add(User(firstName="Arnav", lastName="Jain",email="arnav@utexas.edu", password="test", stocks=[google, apple, signet, aal, tesla], roles=[admin]))
#     #db.session.add(apple)
#     db.session.commit()
#     refreshdb()
#     print 'Initialized the database'

@manager.command
def dropdb():
    if prompt_bool(
        "Are you sure you want to lose all your data"):
        db.drop_all()
        print 'Dropped the database'

@manager.command
def refreshdb():
    # Refresh the score and ranks for each student
    for student in User.query.all():
        numStocks = update_ret(student, student.stocks, student.transactions)
        update_score(student, student.ret, numStocks)

    # Refresh the stored information for each stock
    for stock in Tickers.query.all():
        create_stock_info(stock)
    for stock in Transactions.query.all():
        create_stock_info(stock)


@manager.command
def addstock():
    wb = load_workbook(filename="Workbook1.xlsx")
    ws = wb.active

    symbol = str(raw_input("Ticker: "))
    price = int(raw_input("Starting price: $"))
    num_votes = int(raw_input("How many votes were there? "))

    for index in range(1, num_votes + 1):
        if str(ws['B' + str(index)].value) == 'Long':
            if  Tickers.query.filter_by(short = False, ticker = symbol).count() > 0:
                stock = Tickers.query.filter_by(short = False, ticker = symbol).first()
                print("I FOUND THE STOCK ALREADY")
            else:
                stock = Tickers(ticker=symbol, startingPrice=price, short=False)
        elif str(ws['B' + str(index)].value) == 'Short':
            if Tickers.query.filter_by(short = True, ticker = symbol).count() > 0:
                stock = Tickers.query.filter_by(short = True, ticker = symbol).first()
                print("I FOUND THE STOCK ALREADY")
            else:
                stock = Tickers(ticker=symbol, startingPrice=price, short=True)

        if User.query.filter_by(email=str(ws['A'+str(index)].value)) != None:
            student = User.query.filter_by(email=str(ws['A'+str(index)].value)).first()
            add_stock(student, stock)

if __name__ == '__main__':
    manager.run()
