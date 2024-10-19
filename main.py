from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter

from Scraper import Scraper
from StatusCodes import codes
from Schemas import MetaData
from database import CacheManager

VERSION= "2.2.0"

scraper= Scraper()
cache_manager= CacheManager()
app= FastAPI(title= "getcomics API", version= VERSION)

api_router= APIRouter()

@api_router.get("/")
async def root():

    return {200:codes[200]}

@api_router.get("/search/{query}")
async def search(query: str = None, page: int = 1) -> MetaData:

    filter= {"Query": query, "Page": page}

    cache= cache_manager.fetch_cache(filter)

    if cache != None:

        cache_expired= cache_manager.is_cache_expired(cache["cache_time"])

        if not cache_expired:

            return MetaData(Meta_Data= cache["Comics"]["Meta-Data"])

    scraper.set_search_url(query, page)

    results= await scraper.get_search_results()

    if isinstance(results, int):

        raise HTTPException(status_code= results, detail= codes[results])
    
    if cache == None:
    
        cache_manager.create_cache({"cache_time": None, "Query": query, "Page": page, "Comics": results})

    else:

        cache_manager.update_cache(filter, {"$set":{"cache_time": None, "Comics": results}})

    return MetaData(Meta_Data= results["Meta-Data"])

@api_router.get("/latest")
async def latest() -> MetaData:

    filter= {"Latest": True}
    
    cache= cache_manager.fetch_cache(filter)

    if cache != None:

        cache_expired= cache_manager.is_cache_expired(cache["cache_time"])

        if not cache_expired:

            return MetaData(Meta_Data= cache["Comics"]["Meta-Data"])

    scraper.set_latestpage_url()

    result= await scraper.get_search_results()

    if  cache == None:

        cache_manager.create_cache({"cache_time": None, "Latest": True, "Comics": result})

    else:

        cache_manager.update_cache(filter, {"$set":{"cache_time": None, "Comics": result}})

    return MetaData(Meta_Data= result["Meta-Data"])

@api_router.get("/tag/{tag}")
async def tag(tag: str = None, page: int = 1) -> MetaData:

    filter= {"Tag": tag, "Page": page}

    cache= cache_manager.fetch_cache(filter)

    if cache != None:

        cache_expired= cache_manager.is_cache_expired(cache["cache_time"])

        if not cache_expired:

            return MetaData(Meta_Data= cache["Comics"]["Meta-Data"])

    scraper.set_tag_url(tag, page)

    results= await scraper.get_search_results()

    if isinstance(results, int):

        raise HTTPException(status_code= results, detail= codes[results])
    
    if cache == None:
    
        cache_manager.create_cache({"cache_time": None, "Tag": tag, "Page": page, "Comics": results})

    else:

        cache_manager.update_cache(filter, {"$set":{"cache_time": None, "Comics": results}})

    return MetaData(Meta_Data= results["Meta-Data"])

app.include_router(api_router, prefix= "/getcomics/v2")