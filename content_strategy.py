from typing import List, Literal

from pydantic import BaseModel, Field

from gemini_client import (
    get_gemini_client,
    MODEL,
)


# ---------------------------------
# Content idea structure
# ---------------------------------

class ContentIdea(BaseModel):

    title: str = Field(
        description="SEO-friendly content title"
    )

    primary_keyword: str = Field(
        description="Main SEO keyword for this content"
    )

    supporting_keywords: List[str] = Field(
        description="Related supporting SEO keywords"
    )

    search_intent: Literal[
        "Informational",
        "Navigational",
        "Commercial",
        "Transactional"
    ]

    content_format: Literal[
        "Blog Guide",
        "Listicle",
        "Comparison",
        "Review",
        "Landing Page",
        "Product Page",
        "Tutorial",
        "FAQ"
    ]

    content_angle: str = Field(
        description=(
            "Short explanation of the unique angle "
            "for this piece of content"
        )
    )


# ---------------------------------
# Complete strategy structure
# ---------------------------------

class ContentStrategy(BaseModel):

    target_audience: str = Field(
        description="Primary target audience"
    )

    funnel_stage: Literal[
        "Awareness",
        "Consideration",
        "Conversion"
    ]

    strategy_summary: str = Field(
        description=(
            "Short explanation of the recommended "
            "SEO content strategy"
        )
    )

    content_ideas: List[ContentIdea]

    recommended_outline: List[str] = Field(
        description=(
            "Suggested section headings for the "
            "highest-priority content idea"
        )
    )


# ---------------------------------
# Generate strategy
# ---------------------------------

def generate_content_strategy(
    seed_topic,
    cluster_name,
    cluster_df
):

    client = get_gemini_client()
    
    keyword_lines = []

    for _, row in cluster_df.iterrows():

        keyword_lines.append(
            f"- {row['Keyword']} "
            f"(Intent: {row['Search Intent']}, "
            f"Priority: {row['SEO Priority Score']})"
        )

    keyword_text = "\n".join(
        keyword_lines
    )


    prompt = f"""
    Create an SEO content strategy using the
    keyword research supplied below.

    Seed topic:
    {seed_topic}

    Keyword cluster:
    {cluster_name}

    Keywords:

    {keyword_text}

    Requirements:

    1. Identify the most likely target audience.

    2. Determine the dominant marketing funnel stage.

    3. Explain the overall content strategy briefly.

    4. Generate exactly 5 content ideas.

    5. For every content idea provide:
       - SEO-friendly title
       - primary keyword
       - supporting keywords
       - search intent
       - recommended content format
       - content angle

    6. Prefer keywords supplied in the research.

    7. Do not invent:
       - search volume
       - CPC
       - keyword difficulty
       - traffic estimates
       - ranking positions

    8. Finally create a detailed outline for the
       content idea you consider the strongest
       opportunity.
    """


    interaction = client.interactions.create(

        model=MODEL,

        system_instruction=(
            "You are a senior SEO content strategist. "
            "Turn keyword research into practical "
            "content recommendations. Do not fabricate "
            "SEO metrics or claim access to live "
            "search-engine statistics."
        ),

        input=prompt,

        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ContentStrategy.model_json_schema()
        }
    )


    strategy = ContentStrategy.model_validate_json(
        interaction.output_text
    )

    return strategy