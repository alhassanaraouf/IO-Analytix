from flask import Flask, render_template  # , session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_fontawesome import FontAwesome
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from Sentiment.Database import Client
from Sentiment.Sentiment import Sentiment


db = Client('qabeel', '123456as')
db.connect()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['FONTAWESOME_SERVE_LOCAL'] = True
app.config['FONTAWESOME_STYLES'] = 'all'
Bootstrap(app)
FontAwesome(app)

base = {}
base['name'] = "IO-Analytix"


class KeyForm(FlaskForm):
    key = StringField('Enter Key Word', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     form = NameForm()
#     if form.validate_on_submit():
#         old_name = session.get('name')
#         if old_name is not None and old_name != form.name.data:
#             flash('Looks like you have changed your name!')
#         session['name'] = form.name.data
#         return redirect(url_for('index'))
#     return render_template('index.html', base=base, form=form, name=session.get('name'))

def makedatalist(key):
    temp = []
    cur = db.getData('cleantwitter', key)
    for doc in cur:
        temp.append(doc['text'])
    data = []
    s = Sentiment()
    po = []
    ne = []
    sco = s.ListScore(temp)
    for index, value in enumerate(sco):
        if value['compound'] > 0:
            po.append(temp[index])
        elif value['compound'] < 0:
            ne.append(temp[index])
    data.append(len(temp))
    data.append(len(po))
    data.append(len(ne))
    data.append(sco)
    data.append(po)
    data.append(ne)
    return data


@app.route('/')
def index():
    return render_template('index.html', base=base)


@app.route('/analysis', methods=('GET', 'POST'))
def analysis():
    data = []
    form = KeyForm()
    if form.validate_on_submit():
        data = makedatalist(form.key.data)
        print(data)
    return render_template('analysis.html', base=base, form=form, data=data)
