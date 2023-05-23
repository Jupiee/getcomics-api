from typing import List
from pydantic import BaseModel

class Comic(BaseModel):

    Title: str
    Year: str
    Cover: str
    Size: str
    Description: str

class MetaData(BaseModel):

    Meta_Data: List[Comic]