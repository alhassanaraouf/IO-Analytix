import warnings
import re
import json
import requests
from enchant.checker import SpellChecker
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
warnings.filterwarnings('ignore')


class Cleaning:

    def __init__(self):
        pass

    def Spellcorection(self, text):
        spell = SpellChecker("en_US")
        spell.set_text(text)
        for err in spell:
            err.replace(err.suggest()[0])
        return spell.get_text()

    def preprocess(self, text):

        # Remove username:
        text = re.sub('@[^\s]+', '', text)
        # Remove URLs
        text = re.sub(
            r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', " ", text)
        text = self.Spellcorection(text)
        return text


class Translation:

    def __init__(self):
        pass

    def translate(self, text, to_lang, from_lang=''):
        if from_lang == '':
            from_lang = detect(text)
        api_url = "http://mymemory.translated.net/api/get?q={}&langpair={}|{}".format(
            text, from_lang, to_lang)
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
