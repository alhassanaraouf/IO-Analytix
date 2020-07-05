from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_fontawesome import FontAwesome
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from Sentiment.Database import Client
from Sentiment.Sentiment import Sentiment
from Sentiment import AspectM
from Sentiment.API import TwitterApi
from Sentiment.TextProcessing import Cleaning
from collections import Counter
from werkzeug.security import generate_password_hash, check_password_hash




db = Client("qabeel", "123456as")
db2 = db.connect()
todo = db2.USERS


def updateData(quary):
    data = TwitterApi().Search(quary)
    db2.twitter.insert_many(data, ordered=False)
    return data

def cleanData(key, data=""):
    if not data:
        data = db.getData("twitter", key)
    temp = {}
    temp2 = []
    S = Sentiment()
    c = Cleaning()
    for tweet in data:
        temp["_id"] = tweet["id_str"]
        temp["text"] = c.preprocess(tweet["text"])
        temp["time"] = c.timeProcessing(tweet["created_at"])
        temp["sentiment"] = S.polarity_scores(tweet["text"])["compound"]
        (
            positive_features,
            negative_features,
            neutral_features,
        ) = AspectM.extract_aspects(tweet["text"])
        temp["feature"] = {
            "positive_features": positive_features,
            "negative_features": negative_features,
            "neutral_features": neutral_features,
        }
        print(temp)
        temp2.append(temp)
        try:
            db2.cleantwitter.insert_one(temp)
        except:
            pass
    return temp2

app = Flask(__name__)
app.config["SECRET_KEY"] = "hard to guess string"
app.config["BOOTSTRAP_SERVE_LOCAL"] = True
app.config["FONTAWESOME_SERVE_LOCAL"] = True
app.config["FONTAWESOME_STYLES"] = "all"
Bootstrap(app)
FontAwesome(app)

base = {}
base["name"] = "IO-Analytix"


class KeyForm(FlaskForm):
    key = StringField("Enter Key Word", validators=[DataRequired()])
    realtime = BooleanField("Do You Wanted with Realtime Data (Take Some Time)")
    submit = SubmitField("Submit")


class Key2Form(FlaskForm):
    key = StringField("Enter Key Word", validators=[DataRequired()])
    key2 = StringField("Enter Key Word", validators=[DataRequired()])
    realtime = BooleanField("Do You Wanted with Realtime Data (Take Some Time)")
    submit = SubmitField("Submit")


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


def makedatalist(key, realtime=True):
    if realtime:
        d = updateData(key)
        temp = cleanData(key, d)
    else:
        cur = db.getData("cleantwitter", key)
        temp = []
        for doc in cur:
            temp.append(doc)
    data = []
    po = []
    ne = []
    nu = []
    tags = {'positive': [], "negative": [], "netural": [] }
    tag = []
    tempTag = []
    for x in temp:
        tags["positive"] = tags["positive"]  + x["feature"]["positive_features"]
        tags["negative"] = tags["negative"] + x["feature"]["negative_features"]
        tags["netural"] = tags["netural"] + x["feature"]["neutral_features"]
        if x["sentiment"] > 0:
            po.append(x)
        elif x["sentiment"] < 0:
            ne.append(x)
        else:
            nu.append(x)
    tags["all"] = tags["positive"] + tags["negative"] + tags["netural"]
    ptag = Counter(tags["positive"])
    ntag = Counter(tags["negative"])
    nutag = Counter(tags["netural"])
    c = Counter(tags["all"]).most_common() 
    for x in list(c):
        x = x[0]
        temp = [x, ptag[x], ntag[x], nutag[x], '' ]
        tag.append(temp)
    data.append(len(temp))
    data.append(len(po))
    data.append(len(ne))
    data.append(len(nu))
    data.append(po)
    data.append(ne)
    data.append(nu)
    data.append(tag)
    return data


@app.route("/")
def index():
    return render_template("index.html", base=base, session=session)


@app.route("/profile")
def profile():
    data = {}
    data['history'] =  todo.find_one({ 'username': session['user']  })['history']
    return render_template("profile.html", base=base, session=session, data=data)


@app.route("/analysis", methods=("GET", "POST"))
def analysis():
    data = []
    form = KeyForm()
    if form.validate_on_submit():
        data = makedatalist(form.key.data, form.realtime.data)
        todo.update(
    { 'username': session['user']  }, 
    {'$push': {'history': form.key.data }}
)
    return render_template("analysis.html", base=base, form=form, data=data, session=session)



@app.route("/compare", methods=("GET", "POST"))
def compare():
    data = []
    data2 = []
    form = Key2Form()
    if form.validate_on_submit():
        data = makedatalist(form.key.data, form.realtime.data)
        data2 = makedatalist(form.key2.data, form.realtime.data)
        todo.update_one(
    { 'username': session['user']  }, 
    {'$push': {'history': { '$each': [ form.key.data, form.key2.data] }  }}
)
    return render_template("compare.html", base=base, form=form, data=data, data2=data2 ,session=session)


@app.route('/signin')
def signin():
    if 'user' in session:
        user = session["user"]
        return redirect(url_for('index'))
    return render_template('HOME.html', base=base, session=session)



@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        login_user = todo.find_one({'username': request.form['username']})

        if login_user:
            if check_password_hash(login_user['password'], request.form['password']):
                user= request.form['username']
                session["user"] = user
                return redirect(url_for('signin'))
        else:
            if "user" in session:
                return redirect(url_for('signin'))

        return 'Invalid username/password combination'
    return redirect(url_for('signin'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        existing_user = todo.find_one({'username': request.form['username'
                ]})

        if existing_user is None:
            hashpass = generate_password_hash(request.form['password'])
            temp = {'username': request.form['username'], 'password': hashpass, 'email': request.form['email'], 'fullname': request.form['fullname'], 'history': []}
            todo.insert_one(temp)
            user= request.form['username']
            session["user"] = user
            return redirect(url_for('signin'))

        return 'That username already exists!'

    return render_template('register.html', base=base, session=session)

@app.route('/logout')
def logout():
    session.pop("user",None)
    return redirect(url_for('signin'))


@app.route('/crud')
def CRUD():

	 data = todo.find()
	 return render_template('CRUD.html', todo=data, base=base, session=session)


@app.route('/delete/<string:username>', methods = {'GET'})
def delete(username):
	 flash("Record Has Been Deleted Successfully")
	 todo.delete_one({'username' : username})
	 data = todo.find()
	 return render_template('CRUD.html', todo=data, base=base, session=session)

@app.route('/update/<string:username>',methods=['POST','GET'])
def update(username):

	if request.method == 'POST':
		if todo.find_one({'username': username}):
			return("Username Already Exist")
		todo.update_one( {'username' : username},{'$set': {'fullname': request.form['fullname'], 'email': request.form['email'], 'username': request.form['username']}})

		flash("Data Updated Successfully")
		data = todo.find()
		return redirect(url_for('CRUD'))

