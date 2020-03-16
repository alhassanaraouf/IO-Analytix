from Sentiment.Database import Client
from Sentiment.TextProcessing import Cleaning
from Sentiment.TextProcessing import Translation
from Sentiment.API import TwitterApi
from Sentiment.Sentiment import polarity_scores

test = Client('radwa', '123456as')
test.connect()
print(test.tdata()[0])

text = test.tdata()[0]['text']
test = Cleaning()

print(test.preprocess(text))

test = Translation()

print(test.translate("שמי אל-חסן אשיש", 'en'))

twitter = TwitterApi()
print(twitter.Search('mi', 3, 'en'))
print(twitter.AccountTweets('qabeeljr', 1))

print(polarity_scores("good"))
