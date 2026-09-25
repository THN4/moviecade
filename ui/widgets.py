"""Shared Streamlit widgets for the arcade."""

import streamlit as st

from ui.catalog import movie_titles


@st.cache_data(ttl=300, show_spinner=False)
def available_titles() -> list[str]:
    return movie_titles()


def movie_title_picker(key: str) -> str | None:
    return st.selectbox(
        "Your guess",
        available_titles(),
        index=None,
        placeholder="Start typing a movie title...",
        key=key,
    )
