from pymongo import MongoClient
from dotenv import load_dotenv
import os

client= MongoClient(os.getenv("URI"))

collection= client["cached_comics"]["comics"]
