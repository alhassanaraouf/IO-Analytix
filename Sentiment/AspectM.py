# imports libraries
from Sentiment.Sentiment import Sentiment, Aspects
from nnsplit import NNSplit
import nltk
from nltk.corpus import stopwords
from nltk import pos_tag

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")


def Remove_verbs(text):
    
    """
    Parameters
    ----------
    text : string
        take text as input.

    Returns
    -------
    text : string
        return text erased from all verbs.

    """
    token = nltk.word_tokenize(text) #tokeinze the sentence to group of words
    tuples = pos_tag(token) #pos_tag: take each word and classify it to a particular part of speech based on both its definition and its context then return The tagged tokens 
    text = [word for (word, tag) in tuples if not tag.startswith("V")] # take each second pair in the tuple and check it if it's not verb then return it into the list if it's not.
    text = " ".join(text) #take the list and making join to it
    return text


def Remove_Stopwords(text):
    """
    Parameters
    ----------
    text : string
        take text as input.

    Returns
    -------
    text : string
        return text erased from all stopwords.

    """
    text = text.split() #split the text into words
    text = [word for word in text if not word in set(stopwords.words("english"))] #check if there's stopwords in these words then return it into the list if it's not.
    text = " ".join(text) #take the list and making join to it
    return text


def cleaning(text):
    """
    Parameters
    ----------
    text : string
        take text as input.

    Returns
    -------
    text : string
        return text erased from all verbs and stopwords.

    """
    text = Remove_verbs(text) #apply Remove_verbs function
    text = Remove_Stopwords(text) #apply Remove_Stopwords function
    return text


def normalize(t):
    """
    Take The NNsplit output and transform it to deepsegment like output to work with rest of the code
    
    Parameters
    ----------
    t : list
        list of lists for word and sentences that formed the original text

    Returns
    -------
    normalized : list
    list contains Sentences.
    """   
    temp = []
    for x in t[0]:
        sentences = ""
        for y in x:
            sentences = sentences + y[0] + y[1]
        sentences = sentences.strip()
        temp.append(sentences)
    return temp


def SplitingText(text):
    """
    split text into Sentences
    
    Parameters
    ----------
    text : string
        take text as input.

    Returns
    -------
    normalized : list
    list contains Sentences.
    """    
    splitter = NNSplit("en")
    text = text.replace("but", " ")
    text = [text]
    split_text = splitter.split(text)
    normalized_split_text = normalize(split_text)
    return normalized_split_text


def Sentiment_Texts(text):
    """
    Parameters
    ----------
    text : string
        take text as inpujt.

    Returns
    -------
    list_scores : list
    list contains on a dictionary, each one of thess dictionary contains on a tweet as key and its sentiment as value.
    """
    list_scores = [] #define list
    text_list = SplitingText(text) #apply SplitingText function 
    for i in text_list: #take each text in the list
        tweet = {}   #define dictionary
        i = str(i)   #convert each text to string
        score = Sentiment().polarity_scores(i)  #apply polarity_scores function on text
        score = score["compound"] #calculate the score sentiment of each text
        if score >= 0.05:
            tweet[i] = "positive"
        elif (score > -0.05) and (score < 0.05):
            tweet[i] = "neutral"
        elif score <= -0.05:
            tweet[i] = "negative"
        list_scores.append(tweet)   #After determine the sentiment of each text we append the dictionary that inclue {key "text" :value"sentiment"} in a list.
    return list_scores


def extract_aspects(text):
    """
    Parameters
    ----------
    text : string
        take text as input.

    Returns
    -------
    positive_aspects : list
    list contains on a positive features extracted from cleaned text based on bag of words and the sentiment of that text
    negative_aspects : list
    list contains on a negative features extracted from cleaned text based on bag of words and the sentiment of that text
    neutral_aspects : list
    list contains on a negative features extracted from cleaned text based on bag of words and the sentiment of that text.

    """
    # Define group of lists
    positive_aspects = []
    negative_aspects = []
    neutral_aspects = []
    tweets_list = Sentiment_Texts(text) #Apply Sentiment_Texts function on text 
    for index in range(len(tweets_list)):  
        for key in tweets_list[index]: #take each dictionary in the list
            sentiment = tweets_list[index][key] 
            clean_text = cleaning(key) # apply cleaning function on key of the dictionary 
            for word in clean_text.split(): #split each text to words in loop
                aspects = Aspects().getRelated(word) #return the words if there's in the features aspects in the database.
                if aspects:
                    if sentiment == "positive": # check if the sentiment positive of the text
                        positive_aspects.append(aspects[0]) #then append this aspect in positive_aspects list
                    elif sentiment == "negative": # check if the sentiment negative of the text
                        negative_aspects.append(aspects[0])  #then append this aspect in negative_aspects list
                    elif sentiment == "neutral":  # check if the sentiment neutral of the text
                        neutral_aspects.append(aspects[0])  #then append this aspect in neutral_aspects list

    return positive_aspects, negative_aspects, neutral_aspects
