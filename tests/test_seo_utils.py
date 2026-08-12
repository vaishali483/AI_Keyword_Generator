import pandas as pd

from seo_utils import (
    add_keyword_type,
    add_priority_score,
    add_content_format,
)

from seo_utils import add_keyword_clusters

def create_test_dataframe():

    return pd.DataFrame(
        {
            "Keyword": [
                "running shoes",
                "best running shoes for beginners",
                "buy running shoes online"
            ],
            "Search Intent": [
                "Informational",
                "Commercial",
                "Transactional"
            ]
        }
    )


def test_keyword_type():

    df = create_test_dataframe()

    result = add_keyword_type(df)

    assert (
        result.loc[0, "Keyword Type"]
        == "Short-tail"
    )

    assert (
        result.loc[1, "Keyword Type"]
        == "Long-tail"
    )


def test_priority_score():

    df = create_test_dataframe()

    df = add_keyword_type(df)

    result = add_priority_score(df)

    assert (
        "SEO Priority Score"
        in result.columns
    )

    assert (
        result[
            "SEO Priority Score"
        ].between(
            0,
            100
        ).all()
    )


def test_content_format():

    df = create_test_dataframe()

    result = add_content_format(df)

    assert (
        result.loc[
            1,
            "Recommended Content"
        ]
        == "Comparison / Review"
    )

    assert (
        result.loc[
            2,
            "Recommended Content"
        ]
        == "Landing / Product Page"
    )

def test_keyword_clustering():

    df = pd.DataFrame(
        {
            "Keyword": [
                "digital marketing course",
                "online marketing course",
                "digital marketing agency",
                "marketing agency services"
            ]
        }
    )

    result = add_keyword_clusters(
        df,
        requested_clusters=2
    )

    assert "Cluster" in result.columns

    assert len(result) == 4

    assert (
        result["Cluster"]
        .notna()
        .all()
    )