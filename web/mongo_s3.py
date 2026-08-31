from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017/")
mydb = client["mydatabase"]
mycol = mydb["mycollection"]

