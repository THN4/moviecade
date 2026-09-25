import sys
from pathlib import Path

import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

st.set_page_config(
    page_title="Moviecade", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed"
)

pages = [
    st.Page("pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/box_office.py", title="Box Office Battle", icon="💰"),
    st.Page("pages/poster.py", title="Guess the Poster", icon="🖼️"),
    st.Page("pages/detective.py", title="Movie Detective", icon="🕵️"),
]

st.navigation(pages, position="hidden").run()
