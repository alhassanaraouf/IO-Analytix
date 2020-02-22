from Database import Client
from TextProcessing import Cleaning
from TextProcessing import Translation
from API import TwitterApi
test = Client('radwa', '123456as')
test.connect()
print(test.tdata()[0])

text = test.tdata()[0]['text']
test = Cleaning()

print(test.preprocess(text))

test = Translation('en')

print(test.translate("أنا مندهش لرؤية فقط كيف مثير للدهشة فيدر فائدة!", 'ar'))

twitter = TwitterApi()
print(twitter.Search('mi', 3, 'en'))
print(twitter.AccountTweets('qabeeljr', 1))
