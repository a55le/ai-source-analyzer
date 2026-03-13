from pydantic import BaseModel, HttpUrl


class SourceItem(BaseModel):
    url: HttpUrl
