import asyncio, aiohttp, re
from bs4 import BeautifulSoup

class Scraper:

    def __init__(self):

        self.base_url= "https://getcomics.info"
        self.query= None
        self.page= 0
        self.total_pages= 0

    async def single_page_search(self, query: str, page: int):

        query.replace(" ", "+")
        self.query= query
        self.page= page

        async with aiohttp.ClientSession() as session:

            result = await self.search_page(session)

            return result

    async def search_page(self, session):

        url= f"{self.base_url}/page/{self.page}/?s={self.query}"
        results= await self.fetch_and_filter(session, url)

        return results

    async def fetch_and_filter(self, session, url):

        async with session.get(url) as response:
            
            html= await response.text()

            data= {}

            soup= BeautifulSoup(html, "html.parser")
            articles= soup.find_all("article")
            year_pattern = re.compile(r"\b\d{4}(?:-\d{4})?\b")
            size_pattern= re.compile(r"(\d+\.\d+|\d+)( GB| MB)")

            descriptions= await self.make_tasks(session, articles)
            
            for i, article in enumerate(articles):
                
                title= article.find("h1").find("a").text
                cover= article.find("img")["src"]
                year= re.search(year_pattern, article.find('p').text).group()
                size= re.search(size_pattern, article.find('p').text).group()
                
                data[title]= {
                    "Year": year,
                    "Cover": cover,
                    "Size": size, 
                    "Description": descriptions[i] 
                    }

            return data

    async def make_tasks(self, session, articles):

        description_tasks= [asyncio.ensure_future(self.get_description(article.find("a")["href"], session)) for article in articles]
        descriptions= await asyncio.gather(*description_tasks)
        return descriptions

    async def get_description(self, link, session):

            async with session.get(link) as response:

                response= await response.text()

                soup= BeautifulSoup(response, "html.parser")
                description= soup.find("section", class_= "post-contents").find("p").text
                return description
