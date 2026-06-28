import streamlit as st
from styles import render_header

def get_header():
    title, subtitle = render_header()
    st.markdown(title, unsafe_allow_html=True)
    st.markdown(subtitle, unsafe_allow_html=True)