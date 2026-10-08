import streamlit as st
from views import home, chat, visualization

page = st.sidebar.radio("", ["home", "chat", "visualization"])

if page == "home":
    home.render()
elif page == "chat":
    chat.render()
elif page == "visualization":
    visualization.render()
