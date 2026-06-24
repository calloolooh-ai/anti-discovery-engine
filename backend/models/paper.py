from pydantic import BaseModel


class Paper(BaseModel):
    paper_id: str
    title: str
    abstract: str | None = None
    year: int | None = None
    fields_of_study: list[str] = []
    citation_count: int = 0
    tldr: str | None = None
    concepts: list[str] = []  # extracted bigrams/trigrams
