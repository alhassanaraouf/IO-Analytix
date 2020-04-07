from Sentiment import Sentiment
from Sentiment import Aspects
from deepsegment import DeepSegment
from enchant.checker import SpellChecker
import pymongo
import  pandas as pd
import re
import nltk 
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk import pos_tag



def connenction_db(Database_Name):
    client = pymongo.MongoClient("mongodb+srv://mokbel:123456as@alhassantest-3226x.azure.mongodb.net/test?retryWrites=true&w=majority")
    db = client.GP
    return db[Database_Name]

def get_tweets():
    collection=connenction_db("MobileReviews")
    Data=collection.find({} ,{"text":1 ,"_id":1})
    tweets=pd.DataFrame(Data)
    return tweets

def Remove_verbs(text):
    token=nltk.word_tokenize(text)
    tuples=pos_tag(token)
    text=[word for (word,tag) in tuples if not tag.startswith("V")]
    text=' '.join(text)
    return text
    
def Remove_Stopwords(text):
    text=re.sub('[^a-zA-Z]',' ',text)
    text=text.split()
    text=[word for word in text if not word in set(stopwords.words('english'))]
    text=' '.join(text)
    return text

def cleaning(text):
    text=Remove_verbs(text)
    text=Remove_Stopwords(text)
    return text
    
def Spellcorection(text):
        spell = SpellChecker("en_US")
        spell.set_text(text)
        for err in spell:
            err.replace(err.suggest()[0])
        return spell.get_text()
    
    
def SplitingText(text):
     segmenter = DeepSegment() 
     text=Spellcorection(text)
     text=text.replace("but" , " ")
     split_text=segmenter.segment(text)
     return split_text



     
def Sentiment_Texts(text):
    list_scores=[]
    text_list=SplitingText(text)
    for i in text_list:
        tweet={}
        i=str(i)
        score=Sentiment().polarity_scores(i)
        score = score['compound']
        if (score >=  0.05):
            tweet[i] = 'positive'
        elif (score > -0.05) and (score < 0.05):
            tweet[i] = 'neutral'
        elif (score <= -0.05):
            tweet[i] = 'negative' 
        list_scores.append(tweet)    
    return list_scores
        
def extract_aspects(text):
    positive_aspects=[]
    negative_aspects=[]
    neutral_aspects=[]
    tweets_list=Sentiment_Texts(text)
    for index in range(len(tweets_list)):
       for key in tweets_list[index] :
            sentiment=tweets_list[index][key]
            clean_text=cleaning(key) 
            for word in clean_text.split():
                aspects=Aspects().getRelated(word)
                if aspects:
                    if sentiment== 'positive' :
                       positive_aspects.append(aspects)
                    elif sentiment =='negative'  :
                       negative_aspects.append(aspects)
                    elif sentiment =='neutral'  :
                       neutral_aspects.append(aspects)

    return positive_aspects,negative_aspects ,neutral_aspects                  
   
def summary():
    tweets=get_tweets()
    tweet_list=[]
    for Id,text in zip(tweets['_id'],tweets['text']):
      tweet=dict()
      (positive_features,negative_features,neutral_features)=extract_aspects(text)
      score=Sentiment().polarity_scores(text)
      tweet['id']=Id
      tweet['tweet']=text
      if (score['compound'] >=  0.05):
         tweet['sentiment'] = 'positive'
      elif (score['compound'] > -0.05) and (score['compound'] < 0.05):
         tweet['sentiment'] = 'neutral'
      elif (score['compound'] <= -0.05):
         tweet['sentiment'] = 'negative' 
         
      if positive_features:
          tweet["positive_features"]=positive_features
      elif negative_features :
          tweet["negative_features"]=negative_features
      elif neutral_features :
          tweet["neutral_features"]=neutral_features
          
      tweet_list.append(tweet)
      
    return tweet_list   

