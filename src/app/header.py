import streamlit as st
from styles import render_header

def get_header(DOCUMENTS):
    title, subtitle = render_header(DOCUMENTS)
    st.markdown(title, unsafe_allow_html=True)
    st.markdown(subtitle, unsafe_allow_html=True)