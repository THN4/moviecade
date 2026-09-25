from io import BytesIO

import requests
import streamlit as st
from PIL import Image, ImageFilter
from sqlalchemy.exc import SQLAlchemyError

from ui.game_logic import title_matches
from ui.images import poster_bytes
from ui.repository import poster_movie
from ui.widgets import movie_title_picker


st.page_link("pages/home.py", label="← Back to Home")
st.title("🖼️ Guess the Poster")
st.write("Guess the movie as its poster comes into focus.")

if "poster_round" not in st.session_state:
    st.session_state.poster_round = None
    st.session_state.poster_stage = 0
    st.session_state.poster_result = None
    st.session_state.poster_number = 0
    st.session_state.poster_previous_id = None

if st.session_state.poster_round is None:
    try:
        movie = poster_movie(st.session_state.poster_previous_id)
    except (SQLAlchemyError, ValueError, ModuleNotFoundError) as error:
        st.error("Could not connect to the database. Check .env and start PostgreSQL.")
        st.caption(str(error))
        st.stop()
    if movie is None:
        st.warning("No movie with a poster is available for a new round.")
        st.stop()
    st.session_state.poster_round = movie

movie = st.session_state.poster_round
try:
    image = Image.open(BytesIO(poster_bytes(movie["poster_path"]))).convert("RGB")
except (requests.RequestException, OSError, ValueError):
    st.error("Could not load this poster. Try another movie.")
    if st.button("Try another movie"):
        st.session_state.poster_previous_id = movie["movie_id"]
        st.session_state.poster_round = None
        st.rerun()
    st.stop()

radius = (28, 14, 6, 0)[st.session_state.poster_stage]
with st.container(border=True):
    st.image(image.filter(ImageFilter.GaussianBlur(radius)) if radius else image, width=300)
    st.caption(f"Clarity level {st.session_state.poster_stage + 1}/4")

if st.session_state.poster_result is None:
    try:
        guess = movie_title_picker(
            f"poster_guess_{st.session_state.poster_number}_{st.session_state.poster_stage}"
        )
    except (SQLAlchemyError, ValueError, ModuleNotFoundError) as error:
        st.error("Could not load movie titles from the database.")
        st.caption(str(error))
        st.stop()
    hint, submit = st.columns(2)
    if hint.button("Reveal more", width="stretch", disabled=st.session_state.poster_stage == 3):
        st.session_state.poster_stage += 1
        st.rerun()
    if submit.button("Submit guess", type="primary", width="stretch"):
        if guess is None:
            st.warning("Select a movie title first.")
        elif title_matches(guess, movie["title"]):
            st.session_state.poster_result = True
            st.session_state.poster_stage = 3
            st.rerun()
        elif st.session_state.poster_stage < 3:
            st.session_state.poster_stage += 1
            st.rerun()
        else:
            st.session_state.poster_result = False
            st.rerun()
else:
    if st.session_state.poster_result:
        st.success(f"Correct! The movie is {movie['title']}.")
    else:
        st.error(f"The answer was {movie['title']}.")
    if st.button("Next round", type="primary"):
        st.session_state.poster_previous_id = movie["movie_id"]
        st.session_state.poster_round = None
        st.session_state.poster_stage = 0
        st.session_state.poster_result = None
        st.session_state.poster_number += 1
        st.rerun()
