from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter

from Scraper import Scraper
from StatusCodes import codes
from Schemas import MetaData

VERSION= "2.1.0"

scraper= Scraper()
app= FastAPI(title= "getcomics API", version= VERSION)

api_router= APIRouter()

@api_router.get("/")
async def root():

    return {200:codes[200]}

@api_router.get("/search/{query}")
async def search(query: str = None, page: int = 1) -> MetaData:

    scraper.set_search_url(query, page)

    results= await scraper.get_search_results()

    if isinstance(results, int):

        raise HTTPException(status_code= results, detail= codes[results])

    return MetaData(Meta_Data= results["Meta-Data"])

@api_router.get("/latest")
async def latest() -> MetaData:

    scraper.set_latestpage_url()

    result= await scraper.get_search_results()

    return MetaData(Meta_Data= result["Meta-Data"])

@api_router.get("/tag/{tag}")
async def tag(tag: str = None, page: int = 1) -> MetaData:

    scraper.set_tag_url(tag, page)

    results= await scraper.get_search_results()

    if isinstance(results, int):

        raise HTTPException(status_code= results, detail= codes[results])

    return MetaData(Meta_Data= results["Meta-Data"])

app.include_router(api_router, prefix= "/getcomics/v2")