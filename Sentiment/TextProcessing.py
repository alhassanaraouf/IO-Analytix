import warnings
import re # Regular Expression
import json
import requests
import sqlite3 # used for storing tags (sqlite is small database engine)
from enchant.checker import SpellChecker # Used For Spell Checking and Correction
from langdetect import detect, DetectorFactory # Used For Language Detection
# For Changing The Time Format
from datetime import datetime 
from email.utils import parsedate_tz, mktime_tz


DetectorFactory.seed = 0
warnings.filterwarnings("ignore")


class Cleaning:
    def __init__(self):
        pass

    def Spellcorection(self, text):
        """ Take english text and Correct all the spelling mistakes and return the resualt  """
        client = sqlite3.connect("dict/bagofwords.db")
        db = client.cursor()
        temp = db.execute("SELECT * FROM words").fetchall()
        spell = SpellChecker("en_US")
        with open("dict/privet_dict.txt") as f:
            content = f.readlines()
        for x in content:
            spell.add(x.strip())
        for x in temp:
            spell.add(x[1])
        spell.set_text(text)
        for err in spell:
            if len(err.suggest()) > 0:
                err.replace(err.suggest()[0])
        return spell.get_text()

    def preprocess(self, text):
        """ fix the text for spllings and remove all unnecessary things   """
        # Remove username:
        text = re.sub("@[^\s]+", "", text)
        # Remove Hashtag
        hashtag_re = re.compile("([#][\w_-]+)")
        hashtags = hashtag_re.findall(text)
        if len(hashtags) > 0:
            for x in hashtags:
                temp = x
                temp = temp.replace("#", "").replace("_", " ").replace("-", " ")
                text = text.replace(x, temp)
        # Remove URLs
        text = re.sub(
            r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""",
            " ",
            text,
        )
        text = self.Spellcorection(text)
        return text

    def timeProcessing(self, time):
        """ tranfrorm the twitter data and time format to format a7sn  """
        timestamp = mktime_tz(parsedate_tz(time))
        s = str(datetime.fromtimestamp(timestamp))
        return s


class Translation:
    """ Helper Class When Dealing with Other Langauges the English  """
    def __init__(self):
        pass

    def translate(self, text, to_lang, from_lang=""):
        """ Take Text in Other Languages, then detect the Languages and translated to English  """
        if from_lang == "":
            from_lang = detect(text)
        api_url = "http://mymemory.translated.net/api/get?q={}&langpair={}|{}".format(
            text, from_lang, to_lang
        )
        hdrs = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }
        response = requests.get(api_url, headers=hdrs)
        response_json = json.loads(response.text)
        translation = response_json["responseData"]["translatedText"]
        return translation
