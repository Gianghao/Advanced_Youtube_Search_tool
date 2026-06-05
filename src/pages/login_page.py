import streamlit as st
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent  
sys.path.append(str(src_path))

from authenticate import login_user

st.header("Login page 🔒")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

with st.form("login_form"): #form enter to submit = true    

    email = st.text_input("Email", placeholder="nhập email ở đây 👇")

    password = st.text_input("Password", type='password', placeholder="nhập password ở đây 👇")

    button_clicked = st.form_submit_button("Log in")

if button_clicked:
    name = login_user(email, password)
    if name:
        st.success("login success")
        st.session_state.logged_in = True
        st.session_state.user_email = email
        st.session_state.user_name = name
        st.switch_page("pages/user_page.py")
    else:
        st.error("username or password is incorrect")

st.divider()

st.button("Login with google")