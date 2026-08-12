from typing import List, Literal

from pydantic import BaseModel, Field

from gemini_client import (
    get_gemini_client,
    MODEL,
)


# ---------------------------------
# Structured output models
# ---------------------------------

class KeywordIdea(BaseModel):

    keyword: str = Field(
        description="SEO keyword or search phrase"
    )

    search_intent: Literal[
        "Informational",
        "Navigational",
        "Commercial",
        "Transactional"
    ]


class KeywordResponse(BaseModel):

    keywords: List[KeywordIdea]


# ---------------------------------
# Generate keywords
# ---------------------------------

def generate_keywords(
    topic,
    count=20
):

    prompt = f"""
    Generate approximately {count} useful SEO keywords
    for the following seed topic:

    Topic: {topic}

    Generate a diverse mixture of:

    - broad keywords
    - long-tail keywords
    - question-based searches
    - problem-focused searches
    - comparison searches
    - purchase-focused searches

    Assign exactly one search intent to each keyword.

    Search intent definitions:

    Informational:
    The user wants to learn something.

    Navigational:
    The user wants to reach a particular brand,
    website, company, product, or service.

    Commercial:
    The user is researching or comparing options
    before making a decision.

    Transactional:
    The user is ready to take an action such as
    buying, downloading, booking, subscribing,
    registering, or hiring.

    Avoid duplicate or nearly identical keywords.
    """

    client = get_gemini_client()
    
    interaction = client.interactions.create(

        model=MODEL,

        system_instruction=(
            "You are an SEO keyword research specialist. "
            "Generate realistic search phrases without "
            "inventing search volume, CPC, traffic, or "
            "keyword difficulty statistics."
        ),

        input=prompt,

        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": KeywordResponse.model_json_schema()
        }
    )

    result = KeywordResponse.model_validate_json(
        interaction.output_text
    )

    return [
        keyword.model_dump()
        for keyword in result.keywords
    ]