import streamlit as st
import streamlit.components.v1 as components

# Reads the isolated template file directly to stop text cutoff errors
with open("cube.html", "r", encoding="utf-8") as f:
    html_content = f.read()

components.html(html_content, height=700, scrolling=False)
