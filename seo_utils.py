from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer


def add_keyword_type(df):
    """
    Classify keywords using a simple word-count heuristic.

    1-3 words = Short-tail
    4+ words = Long-tail
    """

    df = df.copy()

    word_counts = df["Keyword"].str.split().str.len()

    df["Keyword Type"] = word_counts.apply(
        lambda count: (
            "Short-tail"
            if count <= 3
            else "Long-tail"
        )
    )

    return df


def add_keyword_clusters(df, requested_clusters=4):
    """
    Group similar keywords using:
    TF-IDF + KMeans clustering.
    """

    df = df.copy()

    if len(df) < 2:
        df["Cluster"] = "General"
        return df

    # Number of clusters cannot exceed
    # number of keywords
    n_clusters = min(
        requested_clusters,
        len(df)
    )

    # Convert keyword text into numerical vectors
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2)
    )

    keyword_vectors = vectorizer.fit_transform(
        df["Keyword"]
    )

    # Train clustering algorithm
    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    cluster_ids = model.fit_predict(
        keyword_vectors
    )

    df["_cluster_id"] = cluster_ids

    # -----------------------------
    # Create readable cluster names
    # -----------------------------

    feature_names = vectorizer.get_feature_names_out()

    cluster_names = {}

    for cluster_id in range(n_clusters):

        cluster_center = model.cluster_centers_[
            cluster_id
        ]

        top_indices = cluster_center.argsort()[
            -2:
        ][::-1]

        top_terms = [
            feature_names[index]
            for index in top_indices
        ]

        cluster_name = " / ".join(
            top_terms
        ).title()

        cluster_names[cluster_id] = cluster_name

    df["Cluster"] = df["_cluster_id"].map(
        cluster_names
    )

    df = df.drop(
        columns=["_cluster_id"]
    )

    return df

def add_priority_score(df):
    """
    Add a simple SEO priority score.

    IMPORTANT:
    This is a heuristic score for demonstration purposes.
    It is NOT real keyword difficulty or search volume data.
    """

    df = df.copy()

    intent_scores = {
        "Informational": 60,
        "Navigational": 45,
        "Commercial": 80,
        "Transactional": 90
    }

    # Start with a score based on search intent
    df["SEO Priority Score"] = (
        df["Search Intent"]
        .map(intent_scores)
        .fillna(50)
    )

    # Give long-tail keywords a small bonus
    long_tail_bonus = (
        df["Keyword Type"] == "Long-tail"
    ).astype(int) * 10

    df["SEO Priority Score"] += long_tail_bonus

    # Keep scores between 0 and 100
    df["SEO Priority Score"] = (
        df["SEO Priority Score"]
        .clip(0, 100)
        .astype(int)
    )

    return df


def add_content_format(df):
    """
    Recommend a content type based on search intent.
    """

    df = df.copy()

    content_map = {
        "Informational": "Blog / Guide",
        "Navigational": "Brand / Resource Page",
        "Commercial": "Comparison / Review",
        "Transactional": "Landing / Product Page"
    }

    df["Recommended Content"] = (
        df["Search Intent"]
        .map(content_map)
        .fillna("General Content")
    )

    return df