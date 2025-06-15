import streamlit as st
import os
import sqlite3
from form import FormController
from dashboard_app import run_dashboard
from setup_db import setup_database

# ✅ Streamlit must set page config before any UI elements
st.set_page_config(page_title="Employee Attrition Portal", layout="wide")

# 📁 Define the path to the SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "attrition.db")

# 🔧 Ensure the database schema is initialized before running
setup_database()


def authenticate_user(emp_id: str, password: str) -> str | None:
    """
    Authenticate the employee using credentials stored in the 'logins' table.

    Args:
        emp_id (str): Employee ID.
        password (str): Plain text password (⚠️ insecure for production use).

    Returns:
        str | None: Authorization level ('admin', 'user') if valid; otherwise None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT password, authorization FROM logins WHERE emp_id = ?",
        (emp_id,),
    )
    record = cursor.fetchone()
    conn.close()

    if record and record[0] == password:
        return record[1]
    return None


def logout() -> None:
    """
    Clears the session state and logs the user out.
    """
    for key in ["logged_in", "emp_id", "auth_level", "admin_page", "form_submitted"]:
        st.session_state.pop(key, None)
    st.rerun()


def main() -> None:
    """
    Main routing logic for the Employee Attrition Streamlit application.
    """
    st.title("🔐 Employee Attrition System")

    # 🌱 Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.emp_id = ""
        st.session_state.auth_level = ""
        st.session_state.admin_page = None
        st.session_state.form_submitted = False

    # 🔐 Login Screen
    if not st.session_state.logged_in:
        st.subheader("Login")
        emp_id = st.text_input("Employee ID")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            auth = authenticate_user(emp_id.strip(), password.strip())
            if auth:
                st.session_state.logged_in = True
                st.session_state.emp_id = emp_id.strip()
                st.session_state.auth_level = auth
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Try again.")

    # ✅ Post-login Routing
    else:
        st.markdown(f"**👤 Logged in as:** `{st.session_state.emp_id}`")

        # 🧑‍💼 Admin Panel
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
                # Admin selected a page
                if st.session_state.admin_page == "Form":
                    form = FormController(
                        emp_id=st.session_state.emp_id, db_path=DB_PATH
                    )
                    form.run()
                    st.session_state.form_submitted = form.submitted

                elif st.session_state.admin_page == "Dashboard":
                    run_dashboard()

                # Back button to main admin menu
                st.markdown("---")
                if st.button("🔙 Back to Admin Menu", key="back_to_menu"):
                    st.session_state.admin_page = None
                    st.session_state.form_submitted = False
                    st.rerun()

        # 👷‍♂️ Employee View (only sees form)
        else:
            form = FormController(emp_id=st.session_state.emp_id, db_path=DB_PATH)
            form.run()
            st.session_state.form_submitted = form.submitted

        # ✅ Logout button appears after successful form submission
        if st.session_state.form_submitted:
            st.markdown("---")
            if st.button("🚪 Logout", key="logout"):
                logout()


if __name__ == "__main__":
    main()
