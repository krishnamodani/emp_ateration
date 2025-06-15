import streamlit as st
import sqlite3
from form import FormController
from dashboard_app import DashboardPage

DB_PATH = "db/employee.db"  # update if needed

# 🔐 Authenticate user using plain text password (no hashing)
def authenticate_user(emp_id, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT authorization FROM logins WHERE emp_id = ? AND password = ?",
        (emp_id, password),
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None  # returns 'admin' or None


# 📄 Login Page UI
def login_ui():
    st.title("🔐 Employee Login")

    emp_id = st.text_input("Employee ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        auth_level = authenticate_user(emp_id, password)
        if auth_level is not None:
            st.session_state.logged_in = True
            st.session_state.emp_id = emp_id
            st.session_state.is_admin = auth_level == "admin"
            st.success("✅ Login successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid Employee ID or Password")


# 🧭 Router for navigation
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_ui()
    else:
        st.sidebar.title("Navigation")

        if st.session_state.is_admin:
            choice = st.sidebar.radio("Select View", ["📋 Fill Survey", "📊 Dashboard"])
            if choice == "📋 Fill Survey":
                FormController(emp_id=st.session_state.emp_id).run()
            elif choice == "📊 Dashboard":
                DashboardPage().render()
        else:
            FormController(emp_id=st.session_state.emp_id).run()

        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.experimental_rerun()


if __name__ == "__main__":
    main()
