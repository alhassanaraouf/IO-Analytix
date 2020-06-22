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

db = Client("qabeel", "123456as")
db2 = db.connect()


def updateData(quary):
    data = TwitterApi().Search(quary)
    print(data)
    db2.twitter.insert_many(data, ordered=False)


def cleanData(key):
    data = db.getData("twitter", key)
    temp = {}
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
        try:
            db2.cleantwitter.insert_one(temp)
        except:
            continue


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
        updateData(key)
        cleanData(key)
    temp = []
    cur = db.getData("cleantwitter", key)
    for doc in cur:
        temp.append(doc)
    data = []
    temp2 = {}
    po = []
    ne = []
    for x in temp:
        print(x)
        temp2["text"] = x["text"]
        temp2["score"] = x["sentiment"]
        temp2["negative_features"] = x["feature"]["negative_features"]
        temp2["positive_features"] = x["feature"]["positive_features"]
        temp2["neutral_features"] = x["feature"]["neutral_features"]
        if temp2["score"] > 0:
            po.append(temp2)
        elif temp2["score"] < 0:
            ne.append(temp2)
    data.append(len(temp))
    data.append(len(po))
    data.append(len(ne))
    data.append(po)
    data.append(ne)
    return data


@app.route("/")
def index():
    return render_template("index.html", base=base)


@app.route("/analysis", methods=("GET", "POST"))
def analysis():
    data = []
    form = KeyForm()
    if form.validate_on_submit():
        print(form.realtime.data)
        data = makedatalist(form.key.data, form.realtime.data)
        print(data)
    return render_template("analysis.html", base=base, form=form, data=data)
