from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter

from Scraper import Scraper
from StatusCodes import codes

import uvicorn

scraper= Scraper()
app= FastAPI(title= "getcomics API", version= "1.0.0")

api_router= APIRouter()

@api_router.get("/")
async def root():

    return {200:codes[200]}

@api_router.get("/search/{query}/{page}")
async def search(query: str = None, page: int = None):

    results= await scraper.single_page_search(query, page)

    if results == {}:

        raise HTTPException(status_code= 101, detail= codes[101])

    return results

app.include_router(api_router, prefix= "/getcomics/v1")

if __name__ == "__main__":

    uvicorn.run(app)
    