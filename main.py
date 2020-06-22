from Sentiment.API import TwitterApi
from Sentiment.Database import Client
from Sentiment.Sentiment import Sentiment, Aspects
from Sentiment.TextProcessing import Cleaning, Translation
from Sentiment import AspectM

print(AspectM.summary())

test = Client("radwa", "123456as")
test.connect()
print(test.getData("twitter")[0])

text = test.tdata()[0]["text"]

test = Cleaning()
text = "Our car insurance is due to be renewsed goooooooooooooooooooooooooooooooooood, in Aprisl! This is what my Apple News feed looks like right-now. #goodpeople #good-people #good_people #gosaam #asdasdasdas :'D :''''''D @alhassanaraouf https://facebook.com oled UMTSs WCDsMA "
print(test.preprocess(text))

test = Translation()

print(test.translate("שמי אל-חסן אשיש", "en"))

twitter = TwitterApi()
print(twitter.Search("mi", 3, "en"))
print(twitter.AccountTweets("qabeeljr", 1))

test = Sentiment()
print(test.polarity_scores("good"))


test = Aspects()
# test.uploadfile()
print(test.getRelated("oled"))
