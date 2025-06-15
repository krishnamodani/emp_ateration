import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import os
import base64


# === Logout Function ===
def logout():
    for key in [
        "logged_in",
        "emp_id",
        "auth_level",
        "admin_page",
        "form_submitted",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


# === Go Back Function ===
def go_back_to_menu():
    st.session_state.admin_page = None
    st.rerun()


# === Fallback for __file__ ===
try:
    base_path = os.path.dirname(__file__)
except NameError:
    base_path = os.getcwd()

DB_PATH = os.path.join(base_path, "data", "attrition.db")


# === Load data from DB ===
def fetch_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        query = """
            SELECT s.*, e.location, e.dept, e.position
            FROM survey_results s
            JOIN employees e ON s.emp_id = e.emp_id
        """
        df = pd.read_sql(query, conn)
        conn.close()

        verdict_map = {
            "1": "Will Leave",
            "2": "Likely to Leave",
            "3": "Not Decided",
            "4": "Less Likely to Leave",
            "5": "Won't Leave",
        }
        df["Final_Verdict"] = df["Final_Verdict"].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


# === Grouped bar chart ===
def plot_grouped_bars(df, question_cols, group_by):
    try:
        grouped = df.groupby(group_by)[question_cols].mean()
        fig, axs = plt.subplots(5, 4, figsize=(22, 18))
        fig.suptitle(f"Average Question Scores by {group_by.title()}", fontsize=20)

        for i, col in enumerate(question_cols):
            ax = axs[i // 4][i % 4]
            grouped[col].plot(kind="bar", ax=ax)
            ax.set_title(col.replace("_", " "), fontsize=10)
            ax.set_ylabel("Avg Score")
            ax.set_xlabel(group_by.title())
            ax.set_ylim(0, 5)
            ax.tick_params(axis="x", labelrotation=45)

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        buf = BytesIO()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)
        return buf
    except Exception as e:
        st.error(f"Error generating grouped bar chart: {e}")
        return BytesIO()


# === Main Dashboard ===
def run_dashboard():
    # --- Buttons at the Top ---

    if st.session_state.get("auth_level") == "admin":
        if st.button("🔙 Back to Admin Menu"):
            go_back_to_menu()
    if st.button("🚪 Logout"):
        logout()

    # --- Title ---
    st.title("📊 Employee Attrition Dashboard")

    df = fetch_data()
    if df.empty:
        return

    with st.sidebar:
        st.header("🔍 Filter Options")
        selected_dept = st.multiselect(
            "Department", df["dept"].unique(), default=list(df["dept"].unique())
        )
        selected_location = st.multiselect(
            "Location", df["location"].unique(), default=list(df["location"].unique())
        )
        selected_position = st.multiselect(
            "Position", df["position"].unique(), default=list(df["position"].unique())
        )

    filtered_df = df[
        (df["dept"].isin(selected_dept))
        & (df["location"].isin(selected_location))
        & (df["position"].isin(selected_position))
    ]

    if filtered_df.empty:
        st.warning("⚠️ No data matches your filter criteria.")
        return

    if st.checkbox("📄 Show Raw Filtered Data"):
        st.dataframe(filtered_df.drop(columns=["emp_id", "srno"]).head(20))

    if "Final_Verdict" in filtered_df.columns:
        st.markdown("### 🥧 Attrition Verdict Distribution")
        verdict_counts = filtered_df["Final_Verdict"].value_counts()
        if not verdict_counts.empty:
            fig_pie = px.pie(
                names=verdict_counts.index,
                values=verdict_counts.values,
                title="Attrition Verdicts",
                color_discrete_sequence=px.colors.sequential.RdBu,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    question_cols = [
        col
        for col in filtered_df.columns
        if col
        not in ["srno", "emp_id", "Final_Verdict", "dept", "location", "position"]
        and pd.api.types.is_numeric_dtype(filtered_df[col])
    ][:20]

    st.markdown("### 📈 Average Scores by Group")
    for group_by in ["location", "position", "dept"]:
        st.subheader(f"Grouped by {group_by.title()}")
        buf = plot_grouped_bars(filtered_df, question_cols, group_by)
        st.image(buf, use_container_width=True)

    st.markdown("### 🔥 Correlation Heatmap")
    try:
        corr = filtered_df[question_cols].corr()
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.heatmap(
            corr, cmap="YlGnBu", annot=True, fmt=".2f", annot_kws={"size": 8}, ax=ax
        )
        buf = BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", dpi=100)
        plt.close()
        buf.seek(0)
        st.image(
            buf, caption="Correlation Between Survey Metrics", use_container_width=True
        )
    except Exception as e:
        st.error(f"Error generating heatmap: {e}")

    st.markdown("### 🚨 HR Attention Required")
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

    for group_by in ["dept", "position", "location"]:
        with st.expander(f"🔎 Alerts by {group_by.title()}"):
            alert_found = False
            for col, meta in alert_columns.items():
                if col in filtered_df.columns:
                    group_means = filtered_df.groupby(group_by)[col].mean()
                    for group, val in group_means.items():
                        if meta["type"] == "low" and val < meta["threshold"]:
                            st.error(f"🚨 {group} has low {meta['label']}: {val:.2f}")
                            alert_found = True
                        elif meta["type"] == "high" and val > meta["threshold"]:
                            st.warning(
                                f"⚠️ {group} shows high {meta['label']}: {val:.2f}"
                            )
                            alert_found = True
            if not alert_found:
                st.info("✅ No alerts triggered based on current thresholds.")

    st.markdown("### 💡 Recommendations to Reduce Attrition")
    st.markdown(
        """
        - Enhance recognition and feedback mechanisms.
        - Promote mentorship and growth opportunities.
        - Foster belonging and collaboration.
        - Improve leadership transparency and support.
        - Run anonymous feedback surveys where trust is low.
    """
    )

    st.markdown("### 📥 Export Data")
    st.download_button(
        "⬇️ Download Filtered Data (CSV)",
        filtered_df.drop(columns=["emp_id", "srno"]).to_csv(index=False),
        file_name="filtered_attrition_data.csv",
    )

    st.markdown("### 📄 Download PDF Report")
    alert_list = []
    for group_by in ["dept", "position", "location"]:
        for col, meta in alert_columns.items():
            if col in filtered_df.columns:
                group_means = filtered_df.groupby(group_by)[col].mean()
                for group, val in group_means.items():
                    if meta["type"] == "low" and val < meta["threshold"]:
                        alert_list.append(
                            f"🚨 {group_by.title()}: {group} has LOW {meta['label']} ({val:.2f})"
                        )
                    elif meta["type"] == "high" and val > meta["threshold"]:
                        alert_list.append(
                            f"⚠️ {group_by.title()}: {group} has HIGH {meta['label']} ({val:.2f})"
                        )

    try:
        with st.spinner("⏳ Generating PDF report..."):
            from report_generator import generate_pdf

            figs = {}
            if "fig_pie" in locals():
                pie_chart_bytes = fig_pie.to_image(format="png")
                figs["verdict_pie"] = base64.b64encode(pie_chart_bytes).decode("utf-8")

            figs["heatmap"] = base64.b64encode(buf.getvalue()).decode("utf-8")

            for group_by in ["location", "position", "dept"]:
                key = f"bar_{group_by}"
                buf = plot_grouped_bars(filtered_df, question_cols, group_by)
                figs[key] = base64.b64encode(buf.getvalue()).decode("utf-8")

            pdf_bytes = generate_pdf(
                summary_text="Auto-generated summary with average scores, visualizations, and alert sections.",
                figs=figs,
                alerts=alert_list,
            )

        if isinstance(pdf_bytes, bytes):
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name="Attrition_Report.pdf",
                mime="application/pdf",
            )
        else:
            st.error("❌ Failed to generate PDF. Please try again.")
    except Exception as e:
        st.error(f"PDF generation failed: {e}")


# === Launch Dashboard ===
if __name__ == "__main__":
    run_dashboard()
