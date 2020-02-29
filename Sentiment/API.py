import requests


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class TwitterApi:
    def __init__(self, bearerkey=""):
        """

        """
        if bearerkey == "":
            bearerkey = "AAAAAAAAAAAAAAAAAAAAAPYXBAAAAAAACLXUNDekMxqa8h%2F40K4moUkGsoc%3DTYfbDKbT3jJPCEVnMYqilB28NHfOPqkca3qaAxGfsyKCs0wRbw"
        self.auth = BearerAuth(bearerkey)
        self.base = "https://api.twitter.com/1.1/"

    def Search(self, quary, NumberOfPages, lang):
        """test"""
        PageCounter = 0
        params = {'q': quary, 'count': 100, 'lang': lang, 'resulty_type': 'recent'}
        api = "search/tweets.json"
        url = self.base + api
        tweets = []
        while PageCounter < NumberOfPages:
            PageCounter += 1
            res = requests.get(url, params=params, auth=self.auth)
            res_json = res.json()['statuses']
            ids = [i['id'] for i in res_json]
            params['max_id'] = min(ids) - 1
            tweets = tweets + res_json
        return tweets

    def AccountTweets(self, AccountName, NumberOfPages):
        """test"""
        PageCounter = 0
        params = {'screen_name': AccountName, 'count': 1, 'exclude_replies': 'true'}
        api = "statuses/user_timeline.json"
        url = self.base + api

        tweets = []
        while PageCounter < NumberOfPages:
            PageCounter += 1
            res = requests.get(url, params=params, auth=self.auth)
            res_json = res.json()
            ids = [i['id'] for i in res_json]
            params['max_id'] = min(ids) - 1
            tweets = tweets + res_json
        return tweets