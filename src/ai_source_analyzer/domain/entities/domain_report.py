from pydantic import BaseModel


class MentionLocation(BaseModel):
    url: str
    query: str


class DomainMentionsReportItem(BaseModel):
    domain: str
    mentions: int
    mentions_in: list[MentionLocation]
