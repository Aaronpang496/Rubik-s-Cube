from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Rubik's Cube", page_icon="🧊", layout="wide")

st.markdown("<style>.block-container {padding-top: 1rem; padding-bottom: 0;}</style>", unsafe_allow_html=True)

try:
    # This tells Streamlit to read the rubiks.html file
    html = Path(__file__).with_name("rubiks.html").read_text(encoding="utf-8")
    
    # We give it a massive height so the 3D canvas has room to render
    components.html(html, height=1050, scrolling=False)
    
except FileNotFoundError:
    st.error("Error: rubiks.html not found. Make sure it is in the same folder as app.py.")
