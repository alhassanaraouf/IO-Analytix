import pymongo


class Client:
    """DataBase Connection and its Methodes to Get Data"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.db = None

    def connect(self, Database="GP"):
        """ get the username and the password passed to the class (and Optionaly the Database You Want To Connect to It) and Connect to It :"DD """
        client = pymongo.MongoClient(
            "mongodb+srv://"
            + self.username
            + ":"
            + self.password
            + "@alhassantest-3226x.azure.mongodb.net/test?retryWrites=true&w=majority"
        )
        self.db = client[Database]
        return self.db

    def getData(self, Platform, Q=""):
        """
        fetch The Data from any Collection in the Connected Database
        Take name of The Collection, and Query 
        Query is Optional if not provided it will fetch last entires
        """
        if Q != "":
            Q = {"$text": {"$search": Q}}
            # Q = '{ $text: { $search: ' + Q + ' } }'
            return list(self.db[Platform].aggregate([{ "$match": Q }, { "$sort": { "created_at": pymongo.DESCENDING, }}, { "$limit": 300 }]))
        else:
            return list(self.db[Platform].find().sort("created_at", pymongo.DESCENDING).limit(300))

    # def getBetaData(self, Platform, Q=""):
    #     """Get PreProcessed Data """
    #     if Q != "":
    #         return(self.db[Platform].find(Q))
    #     else:
    #         return(self.db[Platform].find())
