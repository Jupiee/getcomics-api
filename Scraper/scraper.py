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

    async def single_page_search(self, query: str, page: int):

        query.replace(" ", "+")
        self.query= query
        self.page= page
        self.url= f"{self.base_url}/page/{self.page}/?s={self.query}"

        async with aiohttp.ClientSession() as session:

            self.session = session

            valid_page= await self.is_valid_page()
            cached_data= await self.cached_data("SPS")

            if not cached_data[1] and valid_page:

                result = await self.fetch_and_filter("SPS", cached_data[0])

                return result

            elif cached_data[1] and valid_page:

                return cached_data[0]
            
            else:

                return 202

    async def latest_search(self):

        async with aiohttp.ClientSession() as session:

            self.session= session
            self.url= self.base_url

            cached_data= await self.cached_data("LTS")

            if not cached_data[1]:

                result= await self.fetch_and_filter("LTS", cached_data[0])

                return result
            
            else:

                return cached_data[0]

    async def tag_search(self, tag: str, page: int):
        
        self.query= tag
        self.page= page
        self.url= f"{self.base_url}/cat/{self.query}/page/{self.page}"

        async with aiohttp.ClientSession() as session:

            self.session= session
            valid_page= await self.is_valid_page()
            cached_data= await self.cached_data("TAG")

            if not cached_data[1] and valid_page:

                result= await self.fetch_and_filter("TAG", cached_data[0])

                return result
            
            elif cached_data[1] and valid_page:

                return cached_data[0]
            
            else:

                return 202

    async def fetch_and_filter(self, config, cache):

        async with self.session.get(self.url) as response:
            
            html= await response.text()

            data= {"Meta-Data": []}

            soup= HTMLParser(html)

            try:

                self.articles= soup.css_first("div.post-list-posts").css("article")

            except AttributeError:

                return data
            
            await self.__remove_discord_ad__()

            descriptions= await self.__make_tasks__()

            for i, article in enumerate(self.articles):
                
                title= article.css_first("h1").css_first("a").text()
                cover= article.css_first("img").attributes["src"]
                
                year_and_size = await self.__get_year_size__(article)
                year= year_and_size[0]
                size= year_and_size[1]

                data["Meta-Data"].append({
                    "Title": title,
                    "Year": year,
                    "Cover": cover,
                    "Size": size, 
                    "Description": descriptions[i] 
                    })
            
            await self.insert_or_update(data, cache, config)

            return data

    async def __remove_discord_ad__(self):

        for article in self.articles:

            if "post-145619" in article.attributes["id"]:
                
                self.articles.remove(article)
                break

    async def __get_year_size__(self, article):

        year_pattern = re.compile(r"\b\d{4}(?:-\d{4})?\b")
        size_pattern= re.compile(r"(\d+\.\d+|\d+)( GB| MB)")

        year= re.search(year_pattern, article.css('p')[1].text())
        size= re.search(size_pattern, article.css('p')[1].text())

        if year and size:

            return (year.group(), size.group())

        elif year and not size:
            
            size= "-"
            return (year.group(), size)
        
        elif not year and size:

            year= "-"
            return (year, size.group())
        

    async def __make_tasks__(self):
        
        description_tasks= [asyncio.ensure_future(self.__get_description__(article.css_first("a").attributes["href"])) for article in self.articles]
        descriptions= await asyncio.gather(*description_tasks)
        return descriptions

    async def insert_or_update(self, data, cache, config):

        if config == "SPS":       

            if cache:

                collection.update_one({"Query": self.query, "Page": self.page}, {"$set":{"cache_time": datetime.utcnow() ,"Comics": data}})
            
            elif data["Meta-Data"] != []:

                collection.insert_one({"cache_time": datetime.utcnow(),"Query": self.query, "Page": self.page, "Comics": data})

        elif config == "LTS":

            if cache:

                collection.update_one({"Latest": True}, {"$set":{"cache_time": datetime.utcnow() ,"Comics": data}})

            else:

                collection.insert_one({"cache_time": datetime.utcnow(), "Latest": True, "Comics": data})

        elif config == "TAG":
            
            if cache:

                collection.update_one({"Tag": self.query, "Page": self.page}, {"$set":{"cache_time": datetime.utcnow() ,"Comics": data}})

            elif data["Meta-Data"] != []:

                collection.insert_one({"cache_time": datetime.utcnow(), "Tag": self.query, "Page": self.page, "Comics": data})


    async def __get_description__(self, link):

        async with self.session.get(link) as response:

            response= await response.text()

            soup= HTMLParser(response)
            description= soup.css_first("section.post-contents").css_first("p").text()

            return description
    
    async def is_valid_page(self):

        async with self.session.get(self.url) as response:

            
            if response.status == 404:

                return False
            
            else:

                return True

    async def cached_data(self, config):
        
        cache_time = timedelta(hours=24)
        
        if config == "SPS":

            cache_data= collection.find_one({"Query": self.query, "Page": self.page})

            if cache_data and datetime.utcnow() - cache_data["cache_time"] < cache_time:

                return cache_data["Comics"], True

            else:

                return None, False
            
        elif config == "LTS":

            cache_data= collection.find_one({"Latest": True})

            if cache_data and datetime.utcnow() - cache_data["cache_time"] < cache_time:

                return cache_data["Comics"], True

            else:

                return None, False
            
        elif config == "TAG":

            cache_data= collection.find_one({"Tag": self.query, "Page": self.page})

            if cache_data and datetime.utcnow() - cache_data["cache_time"] < cache_time:

                return cache_data["Comics"], True
            
            else:

                return None, False