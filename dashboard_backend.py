import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import base64
from io import BytesIO


# === Load and Merge Data ===
def load_merged_data(db_path: str) -> pd.DataFrame:
    """
    Connects to the SQLite database and loads merged data from
    'survey_results' and 'employees' tables.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        pd.DataFrame: Merged DataFrame with employee survey data.
    """
    conn = sqlite3.connect(db_path)
    query = """
        SELECT s.*, e.location, e.dept, e.position
        FROM survey_results s
        JOIN employees e ON s.emp_id = e.emp_id
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# === Get Question Columns ===
def get_question_columns(df: pd.DataFrame) -> list:
    """
    Extracts numeric columns representing survey questions,
    excluding known metadata columns.

    Args:
        df (pd.DataFrame): DataFrame to extract columns from.

    Returns:
        list: List of column names.
    """
    exclude = ["emp_id", "srno", "Final_Verdict", "dept", "location", "position"]
    return [
        col
        for col in df.columns
        if col not in exclude and pd.api.types.is_numeric_dtype(df[col])
    ]


# === Generate Visualizations for PDF/Reports ===
def generate_visualizations(df: pd.DataFrame) -> dict:
    """
    Generates key visualizations including grouped bar charts, pie chart,
    and correlation heatmap from the input DataFrame.

    Args:
        df (pd.DataFrame): Cleaned and merged DataFrame.

    Returns:
        dict: Dictionary containing visualizations encoded as base64 strings or plotly objects.
    """
    figs = {}
    question_cols = get_question_columns(df)[:20]
    group_by_options = ["location", "position", "dept"]

    # === Grouped Bar Charts by group_by field ===
    for param in group_by_options:
        grouped = df.groupby(param)[question_cols].mean()
        fig, axs = plt.subplots(5, 4, figsize=(22, 18))
        fig.suptitle(f"Survey Question Scores by {param.title()}", fontsize=20)

        for i, col in enumerate(question_cols):
            ax = axs[i // 4][i % 4]
            grouped[col].plot(kind="bar", ax=ax)
            ax.set_title(col.replace("_", " "), fontsize=10)
            ax.set_xlabel(param.title())
            ax.set_ylabel("Avg Score")
            ax.set_ylim(0, 5)
            ax.tick_params(axis="x", labelrotation=45)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        figs[f"bar_{param}"] = base64.b64encode(buf.read()).decode("utf-8")
        buf.close()
        plt.close()

    # === Pie Chart for Final Verdict ===
    verdict_map = {
        "1": "Will Leave",
        "2": "Likely to Leave",
        "3": "Not Decided",
        "4": "Less Likely to Leave",
        "5": "Won't Leave",
    }
    df["Verdict_Label"] = df["Final_Verdict"].astype(str).map(verdict_map)
    verdict_counts = df["Verdict_Label"].value_counts()

    pie_chart = px.pie(
        names=verdict_counts.index,
        values=verdict_counts.values,
        title="Attrition Verdict Distribution",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    figs["verdict_pie"] = (
        pie_chart  # Not base64-encoded because Plotly handles rendering
    )

    # === Correlation Heatmap of Question Scores ===
    plt.figure(figsize=(14, 8))
    sns.heatmap(
        df[question_cols].corr(),
        cmap="coolwarm",
        annot=True,
        cbar=True,
        annot_kws={"size": 8},
    )
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)
    figs["heatmap"] = base64.b64encode(buf.read()).decode("utf-8")
    buf.close()
    plt.close()

    return figs


# === Generate Alerts from Survey Metrics ===
def generate_alerts(df: pd.DataFrame) -> list:
    """
    Generates alert messages if survey metrics cross threshold values
    that indicate attrition risk or disengagement.

    Args:
        df (pd.DataFrame): Merged DataFrame with employee data.

    Returns:
        list: List of alert strings with warnings.
    """
    alert_columns = {
        "12_Month_Commitment": {
            "type": "low",
            "threshold": 3.0,
            "label": "12-Month Commitment",
        },
        "Job_Search_Thoughts": {
            "type": "high",
            "threshold": 3.5,
            "label": "Job Search Thoughts",
        },
        "Growth_Opportunities": {
            "type": "low",
            "threshold": 3.0,
            "label": "Growth Opportunities",
        },
        "Manager_Trust": {"type": "low", "threshold": 3.0, "label": "Trust in Manager"},
        "Feedback_Received": {
            "type": "low",
            "threshold": 3.0,
            "label": "Feedback Received",
        },
    }

    master_params = ["dept", "position", "location"]
    alerts = []

    for group_by in master_params:
        grouped = df.groupby(group_by)
        for col, meta in alert_columns.items():
            if col in df.columns:
                means = grouped[col].mean()
                for group, score in means.items():
                    if meta["type"] == "low" and score < meta["threshold"]:
                        alerts.append(
                            f"⚠️ {group_by.title()}: {group} has LOW {meta['label']} ({score:.2f})"
                        )
                    elif meta["type"] == "high" and score > meta["threshold"]:
                        alerts.append(
                            f"⚠️ {group_by.title()}: {group} has HIGH {meta['label']} ({score:.2f})"
                        )
    return alerts
