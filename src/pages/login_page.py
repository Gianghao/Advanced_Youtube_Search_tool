import streamlit as st
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent  
sys.path.append(str(src_path))

from authenticate import login_user

st.markdown("""
    <style>
        .stApp {
            background-color: #C2DFFF;
        }
        .stForm{
            background-color: white
            }
        .block-container {
            max-width: 800px;
            padding: 2rem;
            margin: auto;
        }
    </style>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns([6,9,2])
with c2:
    st.header("Login page")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

with st.form("login_form"): #form enter to submit = true    

    email = st.text_input("Email", placeholder="Email")

    password = st.text_input("Password", type='password', placeholder="password")

    c1, c2, c3 = st.columns([7,5,5])
    with c2:
        button_clicked = st.form_submit_button("Log in")

if button_clicked:
    name = login_user(email, password)
    if not email or not password:
        st.warning("Please fill in both fields.")
    elif name:
        st.success("login success")
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.session_state.user_name = name
        st.switch_page("pages/user_page.py")
    else:
        st.error("username or password is incorrect")

