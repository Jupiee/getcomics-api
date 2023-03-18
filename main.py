from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter

from Scraper import Scraper
from StatusCodes import codes

import uvicorn

VERSION= "1.1.0"

scraper= Scraper()
app= FastAPI(title= "getcomics API", version= VERSION)

api_router= APIRouter()

@api_router.get("/")
async def root():

    return {200:codes[200]}

@api_router.get("/search/{query}/{page}")
async def search(query: str = None, page: int = None):

    results= await scraper.single_page_search(query, page)

    if results == {}:

        raise HTTPException(status_code= 201, detail= codes[201])

    return results

app.include_router(api_router, prefix= "/getcomics/v1")

if __name__ == "__main__":

    uvicorn.run(app, host='0.0.0.0', port=8000)
    