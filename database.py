from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import timedelta, datetime
import os, pytz

load_dotenv()

client= MongoClient(os.getenv("URI"))

class CacheManager:

    def __init__(self):

        self.collection= client["cached_comics"]["comics"]
        self.cache_interval= timedelta(hours= 24)
        self.time_zone= pytz.UTC

    def create_cache(self, data):

        cache_time= datetime.now(tz= self.time_zone)

        data["cache_time"]= cache_time

        self.collection.insert_one(data)

    def update_cache(self, filter, updated_data):

        cache_time= datetime.now(tz= self.time_zone)

        updated_data["$set"]["cache_time"]= cache_time

        self.collection.update_one(filter, updated_data)

    def fetch_cache(self, filter):

        return self.collection.find_one(filter)

    def is_cache_expired(self, cache_time):

        cache_time_aware= self.time_zone.localize(cache_time)
        now= datetime.now(self.time_zone)

        if now - cache_time_aware < self.cache_interval:

            return False
        
        return True