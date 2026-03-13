from pydantic import BaseModel, ConfigDict, Field


class MentionLocation(BaseModel):
    url: str
    query: str

class DomainMentionsReportItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    domain: str
    mentions: int
    mentions_in: list[MentionLocation]