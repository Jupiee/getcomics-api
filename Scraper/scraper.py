import asyncio, aiohttp, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database import collection

class Scraper:

    def __init__(self):

        self.base_url= "https://getcomics.info"
        self.query= None
        self.page= 0
        self.total_pages= 0
        self.session= None

    async def single_page_search(self, query: str, page: int):

        query.replace(" ", "+")
        self.query= query
        self.page= page

        async with aiohttp.ClientSession() as session:

            self.session = session

            valid_page= await self.is_valid_page()
            cached_data= await self.cached_data()

            if not cached_data[1] and valid_page:

                result = await self.fetch_and_filter()

                return result

            elif cached_data[1] and valid_page:

                return cached_data[0]
            
            else:

                return 202

    async def fetch_and_filter(self):

        url= f"{self.base_url}/page/{self.page}/?s={self.query}"

        async with self.session.get(url, timeout= 10) as response:
            
            html= await response.text()

            data= {"Meta-Data": []}

            soup= BeautifulSoup(html, "html.parser")
            articles= soup.find_all("article")
            year_pattern = re.compile(r"\b\d{4}(?:-\d{4})?\b")
            size_pattern= re.compile(r"(\d+\.\d+|\d+)( GB| MB)")

            descriptions= await self.make_tasks(articles)
            
            for i, article in enumerate(articles):
                
                title= article.find("h1").find("a").text
                cover= article.find("img")["src"]
                year= re.search(year_pattern, article.find('p').text).group()
                size= re.search(size_pattern, article.find('p').text).group()
                
                data["Meta-Data"].append({
                    "Title": title,
                    "Year": year,
                    "Cover": cover,
                    "Size": size, 
                    "Description": descriptions[i] 
                    })
                
            cache_data= collection.find_one({"Query": self.query, "Page": self.page})

            if cache_data:

                collection.update_one({"Query": self.query, "Page": self.page}, {"$set":{"cache_time": datetime.utcnow() ,"Comics": data}})
            
            elif data["Meta-Data"] != []:

                collection.insert_one({"cache_time": datetime.utcnow(),"Query": self.query, "Page": self.page, "Comics": data})

            return data

    async def make_tasks(self, articles):

        description_tasks= [asyncio.ensure_future(self.get_description(article.find("a")["href"])) for article in articles]
        descriptions= await asyncio.gather(*description_tasks)
        return descriptions

    async def get_description(self, link):

        async with self.session.get(link) as response:

            response= await response.text()

            soup= BeautifulSoup(response, "html.parser")
            description= soup.find("section", class_= "post-contents").find("p").text
            return description
    
    async def is_valid_page(self):

        url= f"{self.base_url}/page/{self.page}/?s={self.query}"

        async with self.session.get(url) as response:

            
            if response.status == 404:

                return False
            
            else:

                return True

    async def cached_data(self):
        
        cache_time = timedelta(hours=24)

        cache_data= collection.find_one({"Query": self.query, "Page": self.page})

        if cache_data and datetime.utcnow() - cache_data["cache_time"] < cache_time:

            return cache_data["Comics"]["Meta-Data"], True

        else:

            return None, False

