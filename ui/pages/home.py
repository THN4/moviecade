import streamlit as st


st.title("🎬 Moviecade")
st.write("Pick a movie trivia game to play.")
st.caption("Movie data and poster images from TMDB.")
st.divider()

games = (
    ("💰 Box Office Battle", "Is the second movie's revenue higher or lower?", "pages/box_office.py"),
    ("🖼️ Guess the Poster", "Identify a movie as its poster comes into focus.", "pages/poster.py"),
    ("🕵️ Movie Detective", "Guess a movie from its genre, studio, and plot clues.", "pages/detective.py"),
)

for column, (title, description, page) in zip(st.columns(3), games):
    with column:
        with st.container(border=True):
            st.subheader(title)
            st.write(description)
            st.page_link(page, label="Play", icon="▶️")
