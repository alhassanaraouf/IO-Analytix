from Sentiment.Database import Client
from Sentiment.TextProcessing import Cleaning
from Sentiment.TextProcessing import Translation
from Sentiment.API import TwitterApi
from Sentiment.Sentiment import Sentiment
from Sentiment.Sentiment import Aspects

test = Client('radwa', '123456as')
test.connect()
print(test.getdata("twitter")[0])

text = test.tdata()[0]['text']

test = Cleaning()
text = "Our car insurance is due to be renewsed goooooooooooooooooooooooooooooooooood, in Aprisl! This is what my Apple News feed looks like right-now. #goodpeople #good-people #good_people #gosaam #asdasdasdas :'D :''''''D @alhassanaraouf https://facebook.com oled UMTSs WCDsMA "
print(test.preprocess(text))

test = Translation()

print(test.translate("שמי אל-חסן אשיש", 'en'))

twitter = TwitterApi()
print(twitter.Search('mi', 3, 'en'))
print(twitter.AccountTweets('qabeeljr', 1))

print(Sentiment.polarity_scores("good"))


test = Aspects()
#test.uploadfile()
print(test.getRelated("oled"))
