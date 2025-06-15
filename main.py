import streamlit as st

# ✅ Must be first Streamlit command
st.set_page_config(page_title="Employee Attrition Portal", layout="wide")

import os
import sqlite3
from form import FormController
from dashboard_app import run_dashboard
from setup_db import setup_database

# 🔧 Ensure database is created and initialized
setup_database()

# 📁 Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "attrition.db")


# 🔐 Authenticate user against login table
def authenticate_user(emp_id, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password, authorization FROM logins WHERE emp_id = ?", (emp_id,)
    )
    record = cursor.fetchone()
    conn.close()
    if record and record[0] == password:
        return record[1]  # e.g., 'admin' or None
    return None


# 🚪 Logout logic
def logout():
    for key in ["logged_in", "emp_id", "auth_level", "admin_page", "form_submitted"]:
        st.session_state.pop(key, None)
    st.rerun()


# 🚀 Main App
def main():
    st.title("🔐 Employee Attrition System")

    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.emp_id = ""
        st.session_state.auth_level = ""
        st.session_state.admin_page = None
        st.session_state.form_submitted = False

    # 🔑 Login Page
    if not st.session_state.logged_in:
        st.subheader("Login")
        emp_id = st.text_input("Employee ID")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            auth = authenticate_user(emp_id.strip(), password.strip())
            if auth is not None:
                st.session_state.logged_in = True
                st.session_state.emp_id = emp_id.strip()
                st.session_state.auth_level = auth
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try again.")

    # ✅ Post-login Views
    else:
        st.markdown(f"**👤 Logged in as:** `{st.session_state.emp_id}`")

        if st.session_state.auth_level == "admin":
            if st.session_state.admin_page is None:
                st.subheader("👋 Welcome Admin")
                st.markdown("Choose an option to proceed:")

                if st.button("📝 Go to Form"):
                    st.session_state.admin_page = "Form"
                    st.rerun()

                if st.button("📊 Go to Dashboard"):
                    st.session_state.admin_page = "Dashboard"
                    st.rerun()

            else:
                if st.session_state.admin_page == "Form":
                    form = FormController(
                        emp_id=st.session_state.emp_id, db_path=DB_PATH
                    )
                    form.run()
                    st.session_state.form_submitted = (
                        form.submitted
                    )  # assume you set `.submitted = True` inside your controller
                elif st.session_state.admin_page == "Dashboard":
                    run_dashboard()

                if st.button("🔙 Back to Admin Menu", key="back_to_menu"):
                    st.session_state.admin_page = None
                    st.session_state.form_submitted = False
                    st.rerun()
        else:
            # Employee user
            form = FormController(emp_id=st.session_state.emp_id, db_path=DB_PATH)
            form.run()
            st.session_state.form_submitted = (
                form.submitted
            )  # you must define this in your form controller

        # ✅ Show Logout button only after form is submitted
        if st.session_state.form_submitted:
            st.markdown("---")
            if st.button("🚪 Logout", key="logout"):
                logout()


if __name__ == "__main__":
    main()
