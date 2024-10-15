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
        
        articles= await self.extract_articles()

        if isinstance(articles, int):

            return articles

        return await self.create_metadata(articles)
    
    async def extract_articles(self):

        response= await self.session.get(self.url)

        parser= LexborHTMLParser(response.text)

        articles= parser.css_first("div.post-list-posts")

        if not articles:

            return 201
        
        return articles.css("article")
    
    async def create_metadata(self, articles):

        data= {"Meta-Data": []}

        description_extraction_coroutines= self.create_couroutines(articles, self.extract_comic_description)
        download_links_extraction_coroutines= self.create_couroutines(articles, self.extract_download_links)

        description_list= await asyncio.gather(*description_extraction_coroutines)
        download_links= await asyncio.gather(*download_links_extraction_coroutines)

        for index, article in enumerate(articles):

            comic_title= article.css_first("h1").css_first("a").text()
            cover_url= article.css_first("img").attributes["src"]

            search_paragraph= article.css("p")[1].text()

            publish_year= self.search_pattern(r"\b\d{4}(?:-\d{4})?\b", search_paragraph)
            file_size= self.search_pattern(r"(\d+\.\d+|\d+)( GB| MB)", search_paragraph)

            data["Meta-Data"].append({

                "Title": comic_title,
                "Year": publish_year,
                "Cover": cover_url,
                "Size": file_size,
                "Description": description_list[index],
                "DownloadLinks": download_links[index]

            })

        return data

    def create_couroutines(self, articles, coroutine_function):

        return [asyncio.ensure_future(coroutine_function(article.css_first("a").attributes["href"])) for article in articles]

    async def extract_comic_description(self, url):

        response= await self.session.get(url)

        parser= LexborHTMLParser(response.text)

        return parser.css_first("section.post-contents").css_first("p").text()
    
    async def extract_download_links(self, url):

        download_links= []

        response= await self.session.get(url)

        parser= LexborHTMLParser(response.text)

        download_buttons= parser.css("div.aio-pulse")

        if not download_buttons:

            return
        
        for link in download_buttons:

            download_links.append(link.css_first("a").attributes["href"])

        return download_links
    
    def search_pattern(self, pattern, text):
        
        pattern_object= re.compile(pattern)

        result= re.search(pattern_object, text)

        if not result:

            return "-"
        
        return result.group()