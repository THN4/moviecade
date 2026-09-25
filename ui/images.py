"""Fetch and display TMDB posters used by the arcade."""

import requests
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def poster_bytes(path: str) -> bytes:
    response = requests.get(f"https://image.tmdb.org/t/p/w500{path}", timeout=10)
    response.raise_for_status()
    return response.content


def show_poster(path: str | None, width: int = 220) -> None:
    if not path:
        st.caption("Poster unavailable")
        return

    try:
        st.image(poster_bytes(path), width=width)
    except (requests.RequestException, OSError, ValueError):
        st.caption("Poster unavailable")
