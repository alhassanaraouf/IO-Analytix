from flask import Flask, render_template  # , session, redirect, url_for
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

db = Client("qabeel", "123456as")
db2 = db.connect()


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
    tags = {'positive':[], "negative":[], "netural":[] }
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
    return render_template("index.html", base=base)


@app.route("/analysis", methods=("GET", "POST"))
def analysis():
    data = []
    form = KeyForm()
    if form.validate_on_submit():
        data = makedatalist(form.key.data, form.realtime.data)
    return render_template("analysis.html", base=base, form=form, data=data)
