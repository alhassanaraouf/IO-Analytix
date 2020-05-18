import pymongo


class Client:
    """DataBase Connection and its Methodes to Get Data"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.db = None

    def connect(self, Database="GP"):
        client = pymongo.MongoClient("mongodb+srv://"+self.username+":"+self.password +
                                     "@alhassantest-3226x.azure.mongodb.net/test?retryWrites=true&w=majority")
        self.db = client[Database]
        return self.db

    def getData(self, Platform, Q=""):
        """Get PreProcessed Data """
        if Q != "":
            Q = {
                '$text': {'$search': Q}
            }
            #Q = '{ $text: { $search: ' + Q + ' } }'
            return(self.db[Platform].find(Q, {'text': 1}, limit=100))
        else:
            return(self.db[Platform].find())

    # def getBetaData(self, Platform, Q=""):
    #     """Get PreProcessed Data """
    #     if Q != "":
    #         return(self.db[Platform].find(Q))
    #     else:
    #         return(self.db[Platform].find())
