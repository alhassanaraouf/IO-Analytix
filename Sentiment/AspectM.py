from Sentiment.Sentiment import Sentiment, Aspects
from nnsplit import NNSplit
import nltk
from nltk.corpus import stopwords
from nltk import pos_tag

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")


def Remove_verbs(text):
    token = nltk.word_tokenize(text)
    tuples = pos_tag(token)
    text = [word for (word, tag) in tuples if not tag.startswith("V")]
    text = " ".join(text)
    return text


def Remove_Stopwords(text):
    text = text.split()
    text = [word for word in text if not word in set(stopwords.words("english"))]
    text = " ".join(text)
    return text


def cleaning(text):
    text = Remove_verbs(text)
    text = Remove_Stopwords(text)
    return text


def normalize(t):
    temp = []
    for x in t[0]:
        sentences = ""
        for y in x:
            sentences = sentences + y[0] + y[1]
        sentences = sentences.strip()
        temp.append(sentences)
    return temp


def SplitingText(text):
    splitter = NNSplit("en")
    text = text.replace("but", " ")
    text = [text]
    split_text = splitter.split(text)
    normalized_split_text = normalize(split_text)
    return normalized_split_text


def Sentiment_Texts(text):
    list_scores = []
    text_list = SplitingText(text)
    for i in text_list:
        tweet = {}
        i = str(i)
        score = Sentiment().polarity_scores(i)
        score = score["compound"]
        if score >= 0.05:
            tweet[i] = "positive"
        elif (score > -0.05) and (score < 0.05):
            tweet[i] = "neutral"
        elif score <= -0.05:
            tweet[i] = "negative"
        list_scores.append(tweet)
    return list_scores


def extract_aspects(text):
    positive_aspects = []
    negative_aspects = []
    neutral_aspects = []
    tweets_list = Sentiment_Texts(text)
    for index in range(len(tweets_list)):
        for key in tweets_list[index]:
            sentiment = tweets_list[index][key]
            clean_text = cleaning(key)
            for word in clean_text.split():
                aspects = Aspects().getRelated(word)
                if aspects:
                    if sentiment == "positive":
                        positive_aspects.append(aspects[0])
                    elif sentiment == "negative":
                        negative_aspects.append(aspects[0])
                    elif sentiment == "neutral":
                        neutral_aspects.append(aspects[0])

    return positive_aspects, negative_aspects, neutral_aspects
