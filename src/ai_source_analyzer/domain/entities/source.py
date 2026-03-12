from pydantic import BaseModel, HttpUrl


class SourceItem(BaseModel):
    url: HttpUrl
    domain: str
    title: str | None = None
    position: int | None = None