from pathlib import Path

from streamlit.testing.v1 import AppTest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_FILE = PROJECT_ROOT / "app.py"


def test_app_loads():

    app = AppTest.from_file(
        APP_FILE,
        default_timeout=15
    )

    app.run()

    assert not app.exception

    assert len(app.title) > 0

    assert (
        app.title[0].value
        == "🔎 AI Keyword Generator"
    )

def test_keyword_generation_with_mock(
    monkeypatch
):

    import keyword_generator


    # ---------------------------------
    # Fake Gemini response
    # ---------------------------------

    fake_keywords = [
        {
            "keyword":
                "digital marketing",

            "search_intent":
                "Informational"
        },
        {
            "keyword":
                "digital marketing course",

            "search_intent":
                "Commercial"
        },
        {
            "keyword":
                "best digital marketing course",

            "search_intent":
                "Commercial"
        },
        {
            "keyword":
                "hire digital marketing agency",

            "search_intent":
                "Transactional"
        },
        {
            "keyword":
                "digital marketing agency services",

            "search_intent":
                "Transactional"
        },
        {
            "keyword":
                "how digital marketing works",

            "search_intent":
                "Informational"
        },
    ]


    # ---------------------------------
    # Fake function
    # ---------------------------------

    def fake_generate_keywords(
        topic,
        count
    ):

        return fake_keywords


    # ---------------------------------
    # Replace real Gemini function
    # ---------------------------------

    monkeypatch.setattr(
        keyword_generator,
        "generate_keywords",
        fake_generate_keywords
    )


    # ---------------------------------
    # Start app
    # ---------------------------------

    app = AppTest.from_file(
        APP_FILE,
        default_timeout=15
    )

    app.run()


    # ---------------------------------
    # Enter seed topic
    # ---------------------------------

    app.text_input[0].set_value(
        "digital marketing"
    )

    app.run()


    # ---------------------------------
    # Click Generate Keywords
    # ---------------------------------

    app.button[0].click()

    app.run()


    # ---------------------------------
    # Verify result
    # ---------------------------------

    assert not app.exception

    assert (
        "keyword_results"
        in app.session_state
    )

    results = app.session_state[
        "keyword_results"
    ]

    assert len(results) == 6

    assert "Keyword" in results.columns

    assert (
        "Search Intent"
        in results.columns
    )

    assert (
        "SEO Priority Score"
        in results.columns
    )

    assert "Cluster" in results.columns

def test_empty_topic_warning():

    app = AppTest.from_file(
        APP_FILE,
        default_timeout=15
    )

    app.run()

    app.button[0].click()

    app.run()

    assert not app.exception

    assert len(app.warning) > 0