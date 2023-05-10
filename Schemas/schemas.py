from pydantic import BaseModel

class Comic(BaseModel):

    Title: str
    Year: str
    Cover: str
    Size: str
    Description: str

    class Config:

        schema_extra= {

            "example": {
                "Meta-Data":[{
                    "Title": "Deadpool – Samurai Vol. 1 – 2 (TPB) (2022)",
                    "Year": "2022",
                    "Cover": "https://i0.wp.com/getcomics.info/share/uploads/2023/03/Deadpool-Samurai-Vol.-1-2-TPB-2022.jpg?fit=400%2C600&ssl=1",
                    "Size": "444 MB",
                    "Description": "Deadpool – Samurai Vol. 1 – 2 (TPB) (2022) : Deadpool lands in Tokyo with a bang! Several bangs in a row, actually. Plus a few slashes, a thud, a fwoosh or two, and finally, a huge kaboom! What could possibly go wrong when Iron Man invites Deadpool to the Samurai Squad of the Avengers? After all, Deadpool is just in it for the money… and the trip to Japan. This is fine, right?"
                },]
            }

        }

    