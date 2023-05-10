from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter

from Scraper import Scraper
from StatusCodes import codes

from Schemas import Comic

VERSION= "1.2.1"

scraper= Scraper()
app= FastAPI(title= "getcomics API", version= VERSION)

api_router= APIRouter()

@api_router.get("/")
async def root():

    return {200:codes[200]}

@api_router.get("/search/{query}/{page}")
async def search(query: str = None, page: int = None) -> Comic:

    results= await scraper.single_page_search(query, page)

    if results == 202:

        raise HTTPException(status_code= 202, detail= codes[202])

    elif results["Meta-Data"] == []:

        raise HTTPException(status_code= 201, detail= codes[201])

    return results

@api_router.get("/latest")
async def latest() -> Comic:

    result= await scraper.latest_search()

    return result

app.include_router(api_router, prefix= "/getcomics/v1")