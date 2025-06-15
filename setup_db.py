import sqlite3
import pandas as pd
import os

# Config
DB_NAME = "data/attrition.db"
CSV_EMPLOYEES = "dataset/employees.csv"
CSV_SURVEY = "dataset/survey_results.csv"
CSV_LOGINS = "dataset/logins.csv"

# Schemas
EMPLOYEES_SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (
    emp_id TEXT PRIMARY KEY,
    name TEXT,
    location TEXT,
    dept TEXT,
    manager TEXT,
    phone_number TEXT,
    email_id TEXT,
    position TEXT
);
"""

SURVEY_RESULTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS survey_results (
    srno INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id TEXT,
    Satisfaction_With_Work INTEGER,
    Daily_Motivation INTEGER,
    Role_Alignment INTEGER,
    Recognition INTEGER,
    Growth_Opportunities INTEGER,
    Feedback_Quality INTEGER,
    Career_Goals_Alignment INTEGER,
    Coworker_Respect INTEGER,
    Collaborative_Environment INTEGER,
    Sense_of_Belonging INTEGER,
    Manager_Support INTEGER,
    Leadership_Trust INTEGER,
    Transparent_Communication INTEGER,
    Work_Life_Balance INTEGER,
    Wellbeing INTEGER,
    Workload_Fairness INTEGER,
    "12_Month_Commitment" INTEGER,
    Job_Search_Thoughts INTEGER,
    Retention_If_Offered_Elsewhere INTEGER,
    Overall_Satisfaction INTEGER,
    Final_Verdict TEXT,
    FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
);
"""

LOGINS_SCHEMA = """
CREATE TABLE IF NOT EXISTS logins (
    emp_id TEXT PRIMARY KEY,
    password TEXT,
    authorization TEXT,
    FOREIGN KEY(emp_id) REFERENCES employees(emp_id)
);
"""

# Verdict mapping
VERDICT_MAP = {
    1: "Will Leave",
    2: "Likely To Leave",
    3: "Not Decided",
    4: "Less Likely To Leave",
    5: "Wont Leave"
}

# Utility Functions
def get_table_columns(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    return [(row[1], row[2]) for row in cursor.fetchall()]

def compare_table_schema(expected_columns, actual_columns):
    return expected_columns == actual_columns

# Main setup function
def setup_database():
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # --- Table Creation & Schema Validation ---

    # Employees Table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees'")
    if not cursor.fetchone():
        cursor.execute(EMPLOYEES_SCHEMA)
    else:
        expected_employees = [
            ('emp_id', 'TEXT'), ('name', 'TEXT'), ('location', 'TEXT'),
            ('dept', 'TEXT'), ('manager', 'TEXT'), ('phone_number', 'TEXT'),
            ('email_id', 'TEXT'), ('position', 'TEXT')
        ]
        actual_employees = get_table_columns(cursor, "employees")
        if not compare_table_schema(expected_employees, actual_employees):
            cursor.execute("DROP TABLE IF EXISTS employees")
            cursor.execute(EMPLOYEES_SCHEMA)

    # Survey Results Table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='survey_results'")
    if not cursor.fetchone():
        cursor.execute(SURVEY_RESULTS_SCHEMA)

    # Logins Table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logins'")
    if not cursor.fetchone():
        cursor.execute(LOGINS_SCHEMA)
    else:
        expected_logins = [('emp_id', 'TEXT'), ('password', 'TEXT'), ('authorization', 'TEXT')]
        actual_logins = get_table_columns(cursor, "logins")
        if not compare_table_schema(expected_logins, actual_logins):
            cursor.execute("DROP TABLE IF EXISTS logins")
            cursor.execute(LOGINS_SCHEMA)

    # --- Data Insert/Update ---

    # Employees
    df_csv_employees = pd.read_csv(CSV_EMPLOYEES)
    try:
        df_db_employees = pd.read_sql_query("SELECT * FROM employees", conn)
    except:
        df_db_employees = pd.DataFrame()

    if not df_csv_employees.equals(df_db_employees):
        cursor.execute("DELETE FROM employees")
        df_csv_employees.to_sql("employees", conn, if_exists="append", index=False)
        print("[✔] employees table updated from CSV.")
    else:
        print("[✓] employees table is up to date.")

    # Survey Results (CSV contains only emp_id to Final_Verdict with numeric verdict)
    cursor.execute("SELECT COUNT(*) FROM survey_results")
    if cursor.fetchone()[0] == 0:
        df_survey = pd.read_csv(CSV_SURVEY)

        # Convert numeric Final_Verdict to text
        df_survey["Final_Verdict"] = df_survey["Final_Verdict"].map(VERDICT_MAP)

        # Insert into DB (srno is auto-handled)
        df_survey.to_sql("survey_results", conn, if_exists="append", index=False)
        print("[✔] survey_results inserted from CSV with text verdicts.")
    else:
        print("[✓] survey_results already has data. Skipping.")

    # Logins
    cursor.execute("SELECT COUNT(*) FROM logins")
    if cursor.fetchone()[0] == 0:
        df_logins = pd.read_csv(CSV_LOGINS)
        df_logins["authorization"] = df_logins["authorization"].fillna("").replace("", "employee")
        df_logins.to_sql("logins", conn, if_exists="append", index=False)
        print("[✔] logins inserted with cleaned authorization field.")
    else:
        print("[✓] logins already has data. Skipping.")

    conn.commit()
    conn.close()
    print("[✅] Database setup completed.")

if __name__ == "__main__":
    setup_database()
