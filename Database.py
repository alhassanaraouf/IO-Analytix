import pymongo


class Client:
  """DataBase Connection and its Methodes to Get Data"""

  def __init__(self, username, password):
    self.username = username
    self.password = password

    db = ""
  def connect(self):
    client = pymongo.MongoClient("mongodb+srv://"+self.username+":"+self.password+"@alhassantest-3226x.azure.mongodb.net/test?retryWrites=true&w=majority")
    global db
    db = client.GP
  
  def tdata(self, Q=""):
    """Get Twitter Data"""
    if Q != "":
      return(db.twitter.find(Q))
    else:
      return(db.twitter.find())


  def mdata(self, Q=""):
    """Get Mastodon Data"""
    if Q != "":
      return(db.mastodon.find(Q))
    else:
      return(db.mastodon.find())

  def rdata(self, Q=""):
    """Get Reddit Data"""
    if Q != "":
      return(db.reddit.find(Q))
    else:
      return(db.reddit.find())


