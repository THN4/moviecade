import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from ui.game_logic import revenue_direction
from ui.images import show_poster
from ui.repository import box_office_pair


st.page_link("pages/home.py", label="← Back to Home")
st.title("💰 Box Office Battle")
st.write("Does the second movie have a higher or lower worldwide revenue?")

if "box_round" not in st.session_state:
    st.session_state.box_round = None
    st.session_state.box_streak = 0
    st.session_state.box_result = None

if st.session_state.box_round is None:
    try:
        st.session_state.box_round = box_office_pair()
    except (SQLAlchemyError, ValueError, ModuleNotFoundError) as error:
        st.error("Could not connect to the database. Check .env and start PostgreSQL.")
        st.caption(str(error))
        st.stop()

pair = st.session_state.box_round
if pair is None:
    st.warning("At least two movies with posters and different positive revenues are needed.")
    st.stop()

first, second = pair
st.metric("Current streak", st.session_state.box_streak)
left, right = st.columns(2)
with left, st.container(border=True):
    st.subheader("First movie")
    show_poster(first["poster_path"])
    st.write(first["title"])
    st.metric("Revenue", f"${first['revenue']:,.0f}")
with right, st.container(border=True):
    st.subheader("Second movie")
    show_poster(second["poster_path"])
    st.write(second["title"])
    if st.session_state.box_result is None:
        st.metric("Revenue", "?")
    else:
        st.metric("Revenue", f"${second['revenue']:,.0f}")

if st.session_state.box_result is None:
    higher, lower = st.columns(2)
    choice = None
    if higher.button("Higher revenue", width="stretch"):
        choice = "higher"
    if lower.button("Lower revenue", width="stretch"):
        choice = "lower"
    if choice:
        correct = choice == revenue_direction(first["revenue"], second["revenue"])
        st.session_state.box_streak = st.session_state.box_streak + 1 if correct else 0
        st.session_state.box_result = correct
        st.rerun()
else:
    if st.session_state.box_result:
        st.success("Correct! Your streak continues.")
    else:
        st.error("Incorrect. Your streak has reset.")
    if st.button("Next round", type="primary"):
        st.session_state.box_round = None
        st.session_state.box_result = None
        st.rerun()
