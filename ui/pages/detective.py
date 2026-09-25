import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from ui.game_logic import title_matches
from ui.images import show_poster
from ui.repository import detective_movie
from ui.widgets import movie_title_picker


st.page_link("pages/home.py", label="← Back to Home")
st.title("🕵️ Movie Detective")
st.write("Guess the movie as new clues are revealed.")

if "detective_round" not in st.session_state:
    st.session_state.detective_round = None
    st.session_state.detective_stage = 0
    st.session_state.detective_result = None
    st.session_state.detective_number = 0
    st.session_state.detective_previous_id = None

if st.session_state.detective_round is None:
    try:
        movie = detective_movie(st.session_state.detective_previous_id)
    except (SQLAlchemyError, ValueError, ModuleNotFoundError) as error:
        st.error("Could not connect to the database. Check .env and start PostgreSQL.")
        st.caption(str(error))
        st.stop()
    if movie is None:
        st.warning("A movie with genres, a production company, a plot, and a poster is needed.")
        st.stop()
    st.session_state.detective_round = movie

movie = st.session_state.detective_round
with st.container(border=True):
    st.subheader("Clue 1 · Genres")
    st.write(" · ".join(movie["genres"]))

if st.session_state.detective_stage >= 1:
    with st.container(border=True):
        st.subheader("Clue 2 · Production companies")
        st.write(" · ".join(movie["companies"]))

if st.session_state.detective_stage >= 2:
    with st.container(border=True):
        st.subheader("Clue 3 · Plot")
        overview = movie["overview"].strip()
        st.write(overview[:240] + ("…" if len(overview) > 240 else ""))

if st.session_state.detective_result is None:
    try:
        guess = movie_title_picker(
            f"detective_guess_{st.session_state.detective_number}_{st.session_state.detective_stage}"
        )
    except (SQLAlchemyError, ValueError, ModuleNotFoundError) as error:
        st.error("Could not load movie titles from the database.")
        st.caption(str(error))
        st.stop()
    hint, submit, skip = st.columns(3)
    if hint.button("Reveal next clue", width="stretch", disabled=st.session_state.detective_stage == 2):
        st.session_state.detective_stage += 1
        st.rerun()
    if submit.button("Submit guess", type="primary", width="stretch"):
        if guess is None:
            st.warning("Select a movie title first.")
        elif title_matches(guess, movie["title"]):
            st.session_state.detective_result = True
            st.rerun()
        elif st.session_state.detective_stage < 2:
            st.session_state.detective_stage += 1
            st.rerun()
        else:
            st.session_state.detective_result = False
            st.rerun()
    if skip.button("Skip movie", width="stretch"):
        st.session_state.detective_result = "skipped"
        st.rerun()
else:
    if st.session_state.detective_result is True:
        st.success(f"Correct! The movie is {movie['title']}.")
    elif st.session_state.detective_result == "skipped":
        st.info(f"Skipped. The movie was {movie['title']}.")
    else:
        st.error(f"The answer was {movie['title']}.")
    show_poster(movie["poster_path"], width=240)
    if st.button("Next round", type="primary"):
        st.session_state.detective_previous_id = movie["movie_id"]
        st.session_state.detective_round = None
        st.session_state.detective_stage = 0
        st.session_state.detective_result = None
        st.session_state.detective_number += 1
        st.rerun()
