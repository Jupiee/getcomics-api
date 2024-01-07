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

            if (cached_data[0] and cached_data[1]) and valid_page:

                return cached_data[0]
            
            elif ((cached_data[0] or cached_data[0] == None) and cached_data[1] == False) and valid_page:

                result= await self.fetch_and_filter("SPS", cached_data)

                return result

            else:

                return 202

    async def latest_search(self):

        async with aiohttp.ClientSession() as session:

            self.session= session
            self.url= self.base_url

            cached_data= await self.cached_data("LTS")

            if not cached_data[0] and cached_data[1]:

                return cached_data[0]
            
            elif (cached_data[0] or cached_data[0] == None) and cached_data[1] == False:

                result= await self.fetch_and_filter("LTS", cached_data)

                return result

    async def tag_search(self, tag: str, page: int):
        
        self.query= tag
        self.page= page
        self.url= f"{self.base_url}/cat/{self.query}/page/{self.page}"

        async with aiohttp.ClientSession() as session:

            self.session= session
            valid_page= await self.is_valid_page()
            cached_data= await self.cached_data("TAG")

            if (cached_data[0] and cached_data[1]) and valid_page:

                return cached_data[0]
            
            elif ((cached_data[0] or cached_data[0] == None) and cached_data[1] == False) and valid_page:

                result= await self.fetch_and_filter("TAG", cached_data)

                return result
            
            else:

                return 202

    async def fetch_and_filter(self, config, cache):

        async with self.session.get(self.url) as response:
            
            html= await response.text()

            data= {"Meta-Data": []}

            soup= HTMLParser(html)
            
            list_of_articles= soup.css_first("div.post-list-posts")

            if list_of_articles:

                self.articles= list_of_articles.css("article")

            else:

                return data
            
            await self.__remove_discord_ad__()

            descriptions= await self.__make_tasks__()
            download_links= await self.__gather_download_links__()

            for i, article in enumerate(self.articles):
                
                title= article.css_first("h1").css_first("a").text()
                cover= article.css_first("img").attributes["src"]
                
                year_and_size = await self.__get_year_and_size__(article)
                year= year_and_size[0]
                size= year_and_size[1]

                data["Meta-Data"].append({
                    "Title": title,
                    "Year": year,
                    "Cover": cover,
                    "Size": size, 
                    "Description": descriptions[i],
                    "DownloadLinks": download_links[i]
                    })
            
            await self.insert_or_update(data, cache, config)

            return data

    async def __remove_discord_ad__(self):

        self.articles = [article for article in self.articles if "post-145619" not in article.attributes["id"]]

    async def __get_year_and_size__(self, article):

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

    async def __gather_download_links__(self):

        links_tasks= [asyncio.ensure_future(self.__get_download_links__(article.css_first("a").attributes["href"])) for article in self.articles]
        download_links= await asyncio.gather(*links_tasks)

        return download_links
    
    async def __get_download_links__(self, link):

        download_links= []

        async with self.session.get(link) as response:

            response= await response.text()

            soup= HTMLParser(response)
            raw_download_links= soup.css("div.aio-pulse")

            if raw_download_links:

                for link in raw_download_links:

                    download_links.append(link.css_first("a").attributes["href"])

        return download_links

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

            cache_query= {"Query": self.query, "Page": self.page}
            
        elif config == "LTS":

            cache_query= {"Latest": True}
            
        elif config == "TAG":

            cache_query= {"Tag": self.query, "Page": self.page}

        cache_data= collection.find_one(cache_query)

        if cache_data and (datetime.utcnow() - cache_data["cache_time"]) < cache_time:

            return cache_data["Comics"], True
        
        elif cache_data and (datetime.utcnow() - cache_data["cache_time"]) > cache_time:

            return cache_data["Comics"], False

        else:

            return None, False