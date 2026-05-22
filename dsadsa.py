import streamlit as st

st.header("Login page 🔒")

with st.form("login_form"): #form enter to submit = true    

    username = st.text_input("Username", placeholder="nhập username ở đây 👇")

    password = st.text_input("Password", type='password', placeholder="nhập password ở đây 👇")

    button_clicked = st.form_submit_button("Loading")

if button_clicked:
    if username == 'admin' and password == 'admin':
        st.success('helu admin', icon='🙋‍♂️')
    else:
        st.error("username or password is incorrect")

st.divider()

st.button("Login with google")