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

    results= await scraper.get_search_results(query, page)

    if isinstance(results, int):

        raise HTTPException(status_code= results, detail= codes[results])

    return MetaData(Meta_Data= results["Meta-Data"])

@api_router.get("/latest")
async def latest() -> MetaData:

    result= await scraper.latest_search()

    return MetaData(Meta_Data= result["Meta-Data"])

@api_router.get("/tag/{tag}")
async def tag(tag: str = None, page: int = 1) -> MetaData:

    results= await scraper.tag_search(tag, page)

    if results == 202:

        raise HTTPException(status_code= 202, detail= codes[202])
    
    elif results["Meta-Data"] == []:

        raise HTTPException(status_code= 201, detail= codes[201])

    return MetaData(Meta_Data= results["Meta-Data"])

app.include_router(api_router, prefix= "/getcomics/v2")