from pymongo import MongoClient

client= MongoClient("mongodb+srv://Jupie:tigerness@cluster0.np31lmg.mongodb.net/?retryWrites=true&w=majority")

collection= client["cached_comics"]["comics"]
