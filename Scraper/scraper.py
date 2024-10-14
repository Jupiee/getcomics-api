import asyncio, re, httpx
from selectolax.lexbor import LexborHTMLParser
from datetime import datetime, timedelta
from database import collection

class Scraper:

    def __init__(self):

        self.base_url= "https://getcomics.org"
        self.url= None
        #self.total_pages= 0
        self.articles= None
        self.session= httpx.AsyncClient()

    async def get_search_results(self, query, page):

        self.url= f"{self.base_url}/page/{page}/?s={query}"

        response= await self.session.get(self.url)

        is_valid_page= response.status_code != 404

        if not is_valid_page:
        
            return 202
        
        return await self.extract_articles()
    
    async def extract_articles(self):

        data= {"Meta-Data": []}

        response= await self.session.get(self.url)

        parser= LexborHTMLParser(response.text)

        articles= parser.css_first("div.post-list-posts")

        if not articles:

            return 201
        
        articles= articles.css("article")

        return articles