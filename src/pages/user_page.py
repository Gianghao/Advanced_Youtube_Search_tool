import streamlit as st
from authenticate import change_password, change_email

st.header("Home")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Bạn chưa đăng nhập!")
    st.switch_page("streamlit_app.py")

email = st.session_state.get("user_email", "")
name = st.session_state.get("user_name", "you")

# ====================== AVATAR + MENU ======================
col1, col2, col3 = st.columns([1, 4, 1])

with col1:  
    avatar_url = st.session_state.get("avatar_url", "https://www.w3schools.com/w3images/avatar2.png")
    
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="{avatar_url}" 
                 style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; 
                        border: 4px solid #4CAF50; cursor: pointer;"
                 onclick="document.getElementById('avatar_menu').click()">
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.title(f"Hello, {name}")

with st.popover("Menu", use_container_width=True):
    st.write("### Account")
    
    if st.button("⚙ Settings", use_container_width=True):
        st.session_state.show_settings = True
    
    if st.button("🚪 Log out", use_container_width=True, type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Logged out!")
        st.switch_page("pages/login_page.py")

            #SETTINGS
if st.session_state.get("show_settings", False):
    st.divider()
    st.write(f"**Email:** {email}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Change email", use_container_width=True):
            st.session_state.settings_mode = "change_email"
    with col2:
        if st.button("Change password", use_container_width=True):
            st.session_state.settings_mode = "change_password"

    #MODE ĐỔI EMAIL
    if st.session_state.get("settings_mode") == "change_email":
        st.divider()
        with st.form("change_email_form"):
            new_email = st.text_input("New email")
            current_password = st.text_input("Enter current password:", type="password")

            col_a, col_b = st.columns(2)
            with col_a:
                submitted = st.form_submit_button("💾Confirm changes", type="primary")
            with col_b:
                cancelled = st.form_submit_button("Cancel", type="secondary")

        if submitted:
            if new_email != email and change_email(email, new_email, current_password):
                st.success("You changed your email successfully!")
                st.session_state.user_email = new_email
                st.session_state.settings_mode = None
                st.rerun()
            else:
                st.error("Failed, check your password")
        if cancelled:
            st.session_state.settings_mode = None
            st.rerun()

    #MODE ĐỔI MẬT KHẨU
    elif st.session_state.get("settings_mode") == "change_password":
        st.divider()
        with st.form("change_password_form"):
            current_password = st.text_input("current password", type="password")
            new_password = st.text_input("new password", type="password")
            confirm_password = st.text_input("repeat new password", type="password")

            col_a, col_b = st.columns(2)
            with col_a:
                submitted = st.form_submit_button("💾Confirm changes", type="primary")
            with col_b:
                cancelled = st.form_submit_button("Cancel", type="secondary")

        if submitted:
            if new_password != confirm_password:
                st.error("Mật khẩu mới không khớp!")
            elif change_password(email, current_password, new_password):
                st.success("You successfully changed your password")
                st.session_state.settings_mode = None
                st.rerun()
            else:
                st.error("Failed, checked current password")
        if cancelled:
            st.session_state.settings_mode = None
            st.rerun()

    st.divider()
    if st.button("⬅️Close setting", type="secondary"):
        st.session_state.show_settings = False
        st.session_state.settings_mode = None
        st.rerun()