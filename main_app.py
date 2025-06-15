import streamlit as st
import sqlite3
from form import FormController
from dashboard_app import DashboardPage

# Path to the SQLite database
DB_PATH = "db/employee.db"


def authenticate_user(emp_id: str, password: str) -> str | None:
    """
    Authenticate the user using plain text password (insecure in production!).

    Args:
        emp_id (str): The employee's ID.
        password (str): The employee's password.

    Returns:
        str | None: Returns the user's authorization level ('admin') if valid, otherwise None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT authorization FROM logins WHERE emp_id = ? AND password = ?",
        (emp_id, password),
    )
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def login_ui() -> None:
    """
    Render the login UI for employee authentication.
    Updates session state upon successful login.
    """
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


def main() -> None:
    """
    Main routing function for the Streamlit app.
    Displays login screen or navigates between the survey and dashboard.
    """
    # Initialize session state on first load
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
            # Normal employees directly see the survey
            FormController(emp_id=st.session_state.emp_id).run()

        if st.sidebar.button("🚪 Logout"):
            st.session_state.clear()
            st.experimental_rerun()


if __name__ == "__main__":
    main()
