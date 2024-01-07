from typing import List, Union
from pydantic import BaseModel

class Comic(BaseModel):

    Title: str
    Year: str
    Cover: str
    Size: str
    Description: str
    DownloadLinks: Union[List[str], List[None]]

class MetaData(BaseModel):

    Meta_Data: List[Comic]