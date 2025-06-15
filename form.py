import streamlit as st
import numpy as np
from attrition_framework import AttritionController
import sqlite3


@st.cache_resource
def load_model(model_path):
    controller = AttritionController(csv_path=model_path)
    return controller


class FormController:
    def __init__(self, emp_id, db_path="data/attrition.db"):
        self.emp_id = emp_id
        self.db_path = db_path
        self.model_controller = load_model(
            "dataset/employee_attrition_dataset_text_verdict.csv"
        )
        self.submitted = False

        self.questions = [
            "Do you feel satisfied with the work you do on a daily basis?",
            "Do you feel motivated to do your best at work every day?",
            "Does your current role align well with your skills and interests?",
            "Do you feel recognized and appreciated for your contributions?",
            "Do you have adequate opportunities for growth and advancement in this organization?",
            "Do you receive regular feedback that helps you improve your performance?",
            "Do you believe your career goals can be achieved in this organization?",
            "Do you feel respected and valued by your coworkers?",
            "Does the work environment here promote collaboration and inclusion?",
            "Do you feel like you belong in this organization?",
            "Does your manager support you in your professional development?",
            "Do you trust the leadership of this organization?",
            "Does management communicate openly and transparently?",
            "Are you able to maintain a healthy work-life balance?",
            "Do you feel mentally and physically well at work?",
            "Is your workload manageable and fair?",
            "Do you see yourself working here in the next 12 months?",
            "Do you rarely think about looking for a job elsewhere?",
            "If offered a similar role elsewhere, would you still prefer to stay here?",
            "Are you overall satisfied with your experience in this organization?",
        ]

        self.prediction_map = {
            "Will Leave": 1,
            "Likely To Leave": 2,
            "Not Decided": 3,
            "Less Likely To Leave": 4,
            "Wont Leave": 5,
        }

    def has_already_submitted(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM survey_results WHERE emp_id = ?", (self.emp_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    def save_to_database(self, responses, prediction_text):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO survey_results (
                emp_id,
                Satisfaction_With_Work,
                Daily_Motivation,
                Role_Alignment,
                Recognition,
                Growth_Opportunities,
                Feedback_Quality,
                Career_Goals_Alignment,
                Coworker_Respect,
                Collaborative_Environment,
                Sense_of_Belonging,
                Manager_Support,
                Leadership_Trust,
                Transparent_Communication,
                Work_Life_Balance,
                Wellbeing,
                Workload_Fairness,
                "12_Month_Commitment",
                Job_Search_Thoughts,
                Retention_If_Offered_Elsewhere,
                Overall_Satisfaction,
                Final_Verdict
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (self.emp_id, *responses, prediction_text),
        )
        conn.commit()
        conn.close()

    def run(self):
        st.title("📝 Employee Satisfaction Survey")

        if self.has_already_submitted():
            st.success("✅ You have already submitted your survey. Thank you!")

            if st.session_state.auth_level == "admin":
                if st.button("🔙 Back to Admin Menu"):
                    st.session_state.admin_page = None
                    st.rerun()

            if st.button("🚪 Logout"):
                self.logout()
            st.stop()

        options = {
            "Not Satisfactory": 1,
            "Slightly Satisfactory": 2,
            "Neutral": 3,
            "Satisfactory": 4,
            "Highly Satisfied": 5,
        }

        responses = []
        errors = []

        with st.form("survey_form"):
            st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

            for i, question in enumerate(self.questions, 1):
                st.markdown(
                    f"<div style='font-size:18px; font-weight:600;'>Q{i}. {question}</div>",
                    unsafe_allow_html=True,
                )
                response = st.radio(
                    label="Select your response:",
                    options=list(options.keys()),
                    key=f"q{i}",
                    index=None,
                    horizontal=True,
                )
                if response:
                    responses.append(options[response])
                else:
                    responses.append(None)
                    errors.append(i)

                if i < len(self.questions):
                    st.markdown(
                        "<hr style='border: 1px solid white;'>", unsafe_allow_html=True
                    )

            submitted = st.form_submit_button("Submit")

        if submitted:
            if None in responses:
                st.error(
                    f"⚠️ Please answer all questions before submitting. Missing: {', '.join(f'Q{i}' for i in errors)}"
                )
                st.stop()

            prediction_text = self.model_controller.predict_from_dict(
                dict(zip(self.model_controller.get_features(), responses))
            )

            self.save_to_database(responses, prediction_text)
            st.success(f"✅ Your responses have been recorded.\n")
            # st.info(f"📊 Final Verdict: **{prediction_text}**")

            self.submitted = True

            if st.session_state.auth_level == "admin":
                if st.button("🔙 Back to Admin Menu"):
                    st.session_state.admin_page = None
                    st.rerun()

            if st.button("🚪 Logout"):
                self.logout()

            st.stop()

        st.warning("📌 Please complete and submit the form.")

    def logout(self):
        for key in [
            "logged_in",
            "emp_id",
            "auth_level",
            "admin_page",
            "form_submitted",
        ]:
            st.session_state.pop(key, None)
        st.rerun()
