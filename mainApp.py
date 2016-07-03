from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
import forms
app = Flask(__name__)
app.config['SECRET_KEY'] = '~t\x86\xc9\x1ew\x8bOcX\x85O\xb6\xa2\x11kL\xd1\xce\x7f\x14<y\x9e'

@app.route('/')
@app.route('/login')
def index():
    form = forms.LoginForm()
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
