from typing import Dict
from pydantic import BaseModel, Field

class RatedContent(BaseModel):
    url: str = Field(description="URL of the article")
    score: str = Field(description="Relevancy score of the article")