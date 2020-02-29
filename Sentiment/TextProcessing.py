import nltk
import warnings
import string
import re
import json
import requests
from nltk.corpus import stopwords
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
warnings.filterwarnings('ignore')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')


class Cleaning:

    def __init__(self):
        pass

    def get_wordnet_pos(self, pos_tag):
        if pos_tag.startswith('J'):
            return wordnet.ADJ
        elif pos_tag.startswith('V'):
            return wordnet.VERB
        elif pos_tag.startswith('N'):
            return wordnet.NOUN
        elif pos_tag.startswith('R'):
            return wordnet.ADV
        else:
            return wordnet.NOUN

    def preprocess(self, text):

        # lowercase the text
        text = text.lower()
        # Remove username:
        text = re.sub('@[^\s]+', '', text)
        # remove the words counting just one letter
        text = [t for t in text.split(" ") if len(t) > 1]
        # tokenize the text and remove puncutation
        text = [word.strip(string.punctuation) for word in text]
        # remove all stop words
        stop = stopwords.words('english')
        text = [x for x in text if x not in stop]
        # remove the words that contain numbers
        text = [word for word in text if not any(c.isdigit() for c in word)]

        # remove tokens that are empty
        text = [t for t in text if len(t) > 0]

        # pos tag the text
        pos_tags = pos_tag(text)
        # lemmatize the text
        text = [
            WordNetLemmatizer().lemmatize(t[0], self.get_wordnet_pos(t[1]))
            for t in pos_tags
        ]
        # join all
        text = " ".join(text)
        text = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", text)
        return (text)

    def pos_tag_words(self, text):
        pos_text = nltk.pos_tag(nltk.word_tokenize(text))
        return " ".join([pos + "-" + word for word, pos in pos_text])


class Translation:

    def __init__(self):
        pass

    def translate(self, text, to_lang, from_lang=''):
        if from_lang == '':
            from_lang = detect(text)
        api_url = "http://mymemory.translated.net/api/get?q={}&langpair={}|{}".format(text, from_lang, to_lang)
        hdrs = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        response = requests.get(api_url, headers=hdrs)
        response_json = json.loads(response.text)
        translation = response_json["responseData"]["translatedText"]
        return translation
