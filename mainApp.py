from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)

@app.route('/')
@app.route('/login')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
