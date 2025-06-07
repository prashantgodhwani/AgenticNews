from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class SearchTopic(str, Enum):
    GENERAL = "general"

class SearchDepth(str, Enum):
    BASIC = "basic"
    ADVANCED = "advanced"

class TimeRange(str, Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"

class TavilyApiParams(BaseModel):
    query: str = Field(..., description="The search query for searching articles relevant to AI and software engineering.", min_length=1, max_length=400)
    topic: SearchTopic = Field(default=SearchTopic.GENERAL, description="Search topic - general or news")
    search_depth: SearchDepth = Field(default=SearchDepth.BASIC, description="Search depth - basic or advanced, advanced will return more results but higher costs and takes longer")
    chunks_per_source: int = Field(default=1, description="The number of content chunks to retrieve from each source.", ge=1, le=10)
    max_results: int = Field(default=5, description="Maximum number of results to return", ge=1, le=20)
    time_range: Optional[TimeRange] = Field(default=TimeRange.WEEK, description="The time range back from the current date to filter results. Useful when looking for sources that have published data.")