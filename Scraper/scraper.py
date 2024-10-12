import asyncio, aiohttp, re
from selectolax.parser import HTMLParser
from datetime import datetime, timedelta
from database import collection

class Scraper:

    def __init__(self):

        self.base_url= "https://getcomics.org"
        self.url= None
        self.query= None
        self.page= 0
        #self.total_pages= 0
        self.articles= None
        self.session= None