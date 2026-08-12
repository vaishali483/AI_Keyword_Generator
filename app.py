import re

import pandas as pd
import streamlit as st

from content_strategy import generate_content_strategy
from keyword_generator import generate_keywords

from error_handler import get_friendly_error
from validators import validate_topic
from logger import logger

from seo_utils import (
    add_keyword_clusters,
    add_keyword_type,
    add_priority_score,
    add_content_format,
)


# ---------------------------------
# Page configuration
# ---------------------------------

st.set_page_config(
    page_title="AI Keyword Generator",
    page_icon="🔎",
    layout="wide"
)


# ---------------------------------
# Header
# ---------------------------------

st.title("🔎 AI Keyword Generator")

st.write(
    "Generate, classify, cluster, and export "
    "SEO keyword ideas using Gemini and NLP."
)


# ---------------------------------
# Sidebar settings
# ---------------------------------

st.sidebar.header("Generation Settings")

keyword_count = st.sidebar.slider(
    "Number of keywords",
    min_value=10,
    max_value=30,
    value=20,
    step=5
)

cluster_count = st.sidebar.slider(
    "Number of clusters",
    min_value=2,
    max_value=8,
    value=4
)


# ---------------------------------
# User input
# ---------------------------------

topic = st.text_input(
    "Enter a topic or seed keyword",
    placeholder="Example: digital marketing"
)


# ---------------------------------
# Generate button
# ---------------------------------

if st.button(
    "Generate Keywords",
    type="primary"
):

    is_valid, validation_result = validate_topic(topic)

    if not is_valid:

        st.warning(validation_result)

    else:

        try:

            with st.spinner(
                "Generating and analysing SEO keywords..."
            ):

                # Generate data using Gemini
                keyword_data = generate_keywords(
                    topic,
                    keyword_count
                )

                # Convert Python data into DataFrame
                df = pd.DataFrame(keyword_data)

                # Rename columns
                df = df.rename(
                    columns={
                        "keyword": "Keyword",
                        "search_intent": "Search Intent"
                    }
                )

                # Remove duplicate keywords
                df = df.drop_duplicates(
                    subset=["Keyword"]
                )

                df = df.reset_index(drop=True)

                # Detect short-tail / long-tail
                df = add_keyword_type(df)

                # NLP clustering
                df = add_keyword_clusters(
                    df,
                    cluster_count
                )

                # Add heuristic priority score
                df = add_priority_score(df)

                # Recommend content format
                df = add_content_format(df)

                # Store results so they survive
                # Streamlit reruns
                st.session_state[
                    "keyword_results"
                ] = df

                st.session_state[
                    "seed_topic"
                ] = topic

                # Clear any strategy from a previous topic.
                st.session_state.pop(
                    "content_strategy",
                    None
                )
                st.session_state.pop(
                    "strategy_cluster",
                    None
                )

        except Exception as e:

            st.error(
                get_friendly_error(e)
            )

            logger.exception(
                "Keyword generation failed"
            )


# ---------------------------------
# Display stored results
# ---------------------------------

if "keyword_results" in st.session_state:

    df = st.session_state[
        "keyword_results"
    ]

    st.divider()

    st.subheader(
        f"SEO Analysis: "
        f"{st.session_state['seed_topic']}"
    )


    # ---------------------------------
    # Dashboard metrics
    # ---------------------------------

    metric1, metric2, metric3, metric4 = st.columns(4)

    metric1.metric(
        "Keywords",
        len(df)
    )

    metric2.metric(
        "Search Intents",
        df["Search Intent"].nunique()
    )

    metric3.metric(
        "Clusters",
        df["Cluster"].nunique()
    )

    average_score = round(
        df["SEO Priority Score"].mean(),
        1
    )

    metric4.metric(
        "Avg. Priority Score",
        average_score
    )


    # ---------------------------------
    # Filters
    # ---------------------------------

    st.subheader("Filter Results")

    filter1, filter2 = st.columns(2)

    intent_options = sorted(
        df["Search Intent"]
        .dropna()
        .unique()
        .tolist()
    )

    type_options = sorted(
        df["Keyword Type"]
        .dropna()
        .unique()
        .tolist()
    )


    with filter1:

        selected_intents = st.multiselect(
            "Search Intent",
            options=intent_options,
            default=intent_options
        )


    with filter2:

        selected_types = st.multiselect(
            "Keyword Type",
            options=type_options,
            default=type_options
        )


    # ---------------------------------
    # Apply filters
    # ---------------------------------

    filtered_df = df[
        df["Search Intent"].isin(
            selected_intents
        )
        &
        df["Keyword Type"].isin(
            selected_types
        )
    ]


    # Safe filename version of the seed topic
    safe_topic = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        st.session_state[
            "seed_topic"
        ].strip()
    ).strip("_")

    if not safe_topic:
        safe_topic = "seo_keywords"


    # ---------------------------------
    # Dashboard tabs
    # ---------------------------------

    results_tab, intent_tab, cluster_tab, strategy_tab = st.tabs(
        [
            "📋 Keyword Results",
            "🎯 Search Intent",
            "🧩 Keyword Clusters",
            "🧠 Content Strategy"
        ]
    )

    with results_tab:

        st.subheader("Keyword Results")

        # Sort highest-priority keywords first
        display_df = filtered_df.sort_values(
            by="SEO Priority Score",
            ascending=False
        )

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )

        st.subheader("Top Opportunities")

        top_keywords = display_df.nlargest(
            5,
            "SEO Priority Score"
        )

        st.dataframe(
            top_keywords[
                [
                    "Keyword",
                    "Search Intent",
                    "SEO Priority Score",
                    "Recommended Content"
                ]
            ],
            width="stretch",
            hide_index=True
        )

    with intent_tab:

        st.subheader("Search Intent Distribution")

        intent_counts = (
            filtered_df["Search Intent"]
            .value_counts()
            .rename_axis("Search Intent")
            .reset_index(name="Keywords")
        )

        st.bar_chart(
            intent_counts,
            x="Search Intent",
            y="Keywords"
        )

        st.dataframe(
            intent_counts,
            width="stretch",
            hide_index=True
        )

    with cluster_tab:

        st.subheader("Keyword Cluster Distribution")

        cluster_counts = (
            filtered_df["Cluster"]
            .value_counts()
            .rename_axis("Cluster")
            .reset_index(name="Keywords")
        )

        st.bar_chart(
            cluster_counts,
            x="Cluster",
            y="Keywords"
        )

        st.dataframe(
            cluster_counts,
            width="stretch",
            hide_index=True
        )

    # ---------------------------------
    # Strategy Tab
    # ---------------------------------

    with strategy_tab:

        st.subheader(
            "🧠 AI Content Strategy"
        )

        st.write(
            "Select a keyword cluster and let Gemini "
            "turn your keyword research into a content plan."
        )

        # ---------------------------------
        # Choose cluster
        # ---------------------------------

        available_clusters = sorted(
            df["Cluster"]
            .dropna()
            .unique()
            .tolist()
        )

        if not available_clusters:
            st.info(
                "No keyword clusters are available yet."
            )

        else:
            selected_cluster = st.selectbox(
                "Choose a keyword cluster",
                available_clusters
            )

            # ---------------------------------
            # Get keywords in selected cluster
            # ---------------------------------

            cluster_df = df[
                df["Cluster"] == selected_cluster
            ].copy()

            st.write(
                f"**Keywords in this cluster: "
                f"{len(cluster_df)}**"
            )

            st.dataframe(
                cluster_df[
                    [
                        "Keyword",
                        "Search Intent",
                        "SEO Priority Score"
                    ]
                ],
                width="stretch",
                hide_index=True
            )

            # ---------------------------------
            # Generate strategy
            # ---------------------------------

            if st.button(
                "✨ Generate Content Strategy",
                type="primary"
            ):

                try:
                    with st.spinner(
                        "Gemini is building your "
                        "content strategy..."
                    ):
                        strategy = generate_content_strategy(
                            seed_topic=st.session_state[
                                "seed_topic"
                            ],
                            cluster_name=selected_cluster,
                            cluster_df=cluster_df
                        )

                        st.session_state[
                            "content_strategy"
                        ] = strategy

                        st.session_state[
                            "strategy_cluster"
                        ] = selected_cluster

                except Exception as e:

                    st.error(
                        get_friendly_error(e)
                    )

                    print(
                        f"Content strategy error: {e}"
                    )

            # ---------------------------------
            # Display generated strategy
            # ---------------------------------

            if (
                "content_strategy" in st.session_state
                and
                st.session_state.get(
                    "strategy_cluster"
                ) == selected_cluster
            ):
                strategy = st.session_state[
                    "content_strategy"
                ]

                st.divider()

                # ---------------------------------
                # Strategy overview
                # ---------------------------------

                st.subheader(
                    "Strategy Overview"
                )

                col1, col2 = st.columns(2)

                col1.metric(
                    "Target Audience",
                    strategy.target_audience
                )

                col2.metric(
                    "Funnel Stage",
                    strategy.funnel_stage
                )

                st.write(
                    strategy.strategy_summary
                )

                # ---------------------------------
                # Content ideas
                # ---------------------------------

                st.subheader(
                    "Recommended Content Ideas"
                )

                content_rows = []

                for idea in strategy.content_ideas:
                    content_rows.append(
                        {
                            "Title": idea.title,
                            "Primary Keyword": (
                                idea.primary_keyword
                            ),
                            "Search Intent": (
                                idea.search_intent
                            ),
                            "Format": (
                                idea.content_format
                            ),
                            "Content Angle": (
                                idea.content_angle
                            )
                        }
                    )

                content_df = pd.DataFrame(
                    content_rows
                )

                st.dataframe(
                    content_df,
                    width="stretch",
                    hide_index=True
                )

                # ---------------------------------
                # Content details
                # ---------------------------------

                st.subheader(
                    "Content Details"
                )

                for number, idea in enumerate(
                    strategy.content_ideas,
                    start=1
                ):
                    with st.expander(
                        f"{number}. {idea.title}"
                    ):
                        st.write(
                            f"**Primary Keyword:** "
                            f"{idea.primary_keyword}"
                        )

                        st.write(
                            f"**Search Intent:** "
                            f"{idea.search_intent}"
                        )

                        st.write(
                            f"**Content Format:** "
                            f"{idea.content_format}"
                        )

                        st.write(
                            f"**Content Angle:** "
                            f"{idea.content_angle}"
                        )

                        st.write(
                            "**Supporting Keywords:**"
                        )

                        for keyword in (
                            idea.supporting_keywords
                        ):
                            st.write(
                                f"- {keyword}"
                            )

                # ---------------------------------
                # Recommended outline
                # ---------------------------------

                st.subheader(
                    "Recommended Content Outline"
                )

                for section_number, section in enumerate(
                    strategy.recommended_outline,
                    start=1
                ):
                    st.write(
                        f"{section_number}. {section}"
                    )

                # ---------------------------------
                # Markdown export
                # ---------------------------------

                markdown_content = f"""# SEO Content Strategy

## Seed Topic

{st.session_state["seed_topic"]}

## Keyword Cluster

{selected_cluster}

## Target Audience

{strategy.target_audience}

## Funnel Stage

{strategy.funnel_stage}

## Strategy Summary

{strategy.strategy_summary}

## Content Ideas
"""

                for number, idea in enumerate(
                    strategy.content_ideas,
                    start=1
                ):
                    markdown_content += f"""

### {number}. {idea.title}

**Primary Keyword:** {idea.primary_keyword}

**Search Intent:** {idea.search_intent}

**Content Format:** {idea.content_format}

**Content Angle:** {idea.content_angle}

**Supporting Keywords:**

"""

                    for keyword in (
                        idea.supporting_keywords
                    ):
                        markdown_content += (
                            f"- {keyword}\n"
                        )

                markdown_content += (
                    "\n## Recommended Content Outline\n\n"
                )

                for number, section in enumerate(
                    strategy.recommended_outline,
                    start=1
                ):
                    markdown_content += (
                        f"{number}. {section}\n"
                    )

                safe_cluster = re.sub(
                    r"[^a-zA-Z0-9_-]+",
                    "_",
                    selected_cluster.strip()
                ).strip("_")

                if not safe_cluster:
                    safe_cluster = "cluster"

                st.download_button(
                    label=(
                        "⬇️ Download Content Strategy "
                        "(.md)"
                    ),
                    data=markdown_content.encode(
                        "utf-8"
                    ),
                    file_name=(
                        f"{safe_topic}_"
                        f"{safe_cluster}_"
                        "content_strategy.md"
                    ),
                    mime="text/markdown",
                    on_click="ignore"
                )

    # ---------------------------------
    # CSV export
    # ---------------------------------

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=(
            f"{safe_topic}_seo_keywords.csv"
        ),
        mime="text/csv",
        on_click="ignore"
    )