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