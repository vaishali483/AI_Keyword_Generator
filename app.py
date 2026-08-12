import re

import pandas as pd
import streamlit as st

from keyword_generator import generate_keywords
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

    if not topic.strip():

        st.warning(
            "Please enter a topic or seed keyword."
        )

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

        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
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


    # ---------------------------------
    # Dashboard tabs
    # ---------------------------------

    results_tab, intent_tab, cluster_tab = st.tabs(
        [
            "📋 Keyword Results",
            "🎯 Search Intent",
            "🧩 Keyword Clusters"
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
    # CSV export
    # ---------------------------------

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")


    safe_topic = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        st.session_state[
            "seed_topic"
        ].strip()
    )


    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=(
            f"{safe_topic}_seo_keywords.csv"
        ),
        mime="text/csv",
        on_click="ignore"
    )