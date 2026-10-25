from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Island Flight",
    page_icon="✈️",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

game_path = Path(__file__).resolve().with_name("game.html")

try:
    game_html = game_path.read_text(encoding="utf-8")
except FileNotFoundError:
    st.error(
        "game.html was not found. Save it in the same folder as app.py. "
        "The filename must be game.html, not game.hmtl."
    )
    st.stop()
except (OSError, UnicodeError) as error:
    st.error(f"Could not read game.html: {error}")
    st.stop()

components.html(
    game_html,
    height=1100,
    scrolling=True,
)
