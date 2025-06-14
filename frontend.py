# frontend.py

import streamlit as st

st.set_page_config(
    page_title="Employee Attrition Survey", layout="centered"
)  # Must be first!

import numpy as np
from test import AttritionController


# ---------- CACHED MODEL LOADER ----------
@st.cache_resource
def load_model(model_path):
    controller = AttritionController(data_path=model_path)
    controller.model.load_and_clean_data()
    controller.model.train()
    return controller


# ---------- STATE MANAGER ----------
class SurveySessionState:
    """Singleton-style session state manager."""

    def __init__(self, total_questions):
        self.total_questions = total_questions
        self._init_state()

    def _init_state(self):
        if "current_q" not in st.session_state:
            st.session_state.current_q = 0
        if "responses" not in st.session_state:
            st.session_state.responses = []

    def get_current_question_index(self):
        return st.session_state.current_q

    def add_response(self, value):
        st.session_state.responses.append(value)
        st.session_state.current_q += 1

    def is_complete(self):
        return st.session_state.current_q >= self.total_questions

    def get_responses(self):
        return np.array([st.session_state.responses])

    def reset(self):
        st.session_state.current_q = 0
        st.session_state.responses = []
        for i in range(self.total_questions):
            st.session_state.pop(f"question_{i}", None)


# ---------- VIEW LAYER ----------
class StreamlitSurveyView:
    """Handles UI rendering."""

    def __init__(self, questions):
        self.questions = questions
        self.state = SurveySessionState(total_questions=len(questions))

    def render(self):
        st.title("🧑‍💼 Employee Attrition Survey")

        current = self.state.get_current_question_index()
        total = self.state.total_questions
        percentage = int((current / total) * 100)

        # Determine status label
        if current >= total:
            status_label = "✅ Completed"
            percentage = 100
            display_q = total  # avoid showing 21 of 20
        else:
            status_label = f"📌 Question <strong>{current + 1}</strong> of <strong>{total}</strong>"
            display_q = current + 1

        # HTML/CSS for animated progress bar with moving percentage
        st.markdown(
            f"""
            <style>
            .question-status {{
                font-size: 1.1rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: #333;
            }}

            .progress-container {{
                position: relative;
                width: 90%;
                height: 28px;
                background-color: #f1f1f1;
                border-radius: 20px;
                overflow: hidden;
                margin-bottom: 25px;
            }}

            .progress-bar {{
                height: 100%;
                background: linear-gradient(135deg, #FFA500, #FF8C00);
                width: {percentage}%;
                border-radius: 20px 0 0 20px;
                transition: width 0.5s ease;
                position: relative;
            }}

            .percentage-label {{
                position: absolute;
                top: 50%;
                left: {min(percentage, 97)}%;
                transform: translate(-100%, -50%);
                font-size: 0.85rem;
                font-weight: 600;
                color: #fff;
                text-shadow: 0 0 3px rgba(0,0,0,0.4);
                transition: left 0.5s ease;
                white-space: nowrap;
            }}
            </style>

            <div class="question-status">{status_label}</div>
            <div class="progress-container">
                <div class="progress-bar"></div>
                <div class="percentage-label">{percentage}%</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

        if not self.state.is_complete():
            self.display_question()
            return False
        else:
            self.display_result()
            return True

    def display_question(self):
        idx = self.state.get_current_question_index()
        st.subheader(f"Question {idx + 1}")
        key = f"question_{idx}"

        # --- Display the main question ---
        st.markdown(
            f"<div style='font-size: 24px; font-weight: 600; margin-bottom: 8px;'>{self.questions[idx]}</div>",
            unsafe_allow_html=True,
        )

        # Label map: Display text -> Actual value
        options = {
            "Not Satisfactory": 1,
            "Slightly Satisfactory": 2,
            "Neutral": 3,
            "Satisfactory": 4,
            "Highly Satisfied": 5,
        }

        # Only render the radio if not already answered
        if key not in st.session_state:
            choice = st.radio(
                "Choose your satisfaction level:",
                list(options.keys()),
                index=None,
                key=key,
                label_visibility="collapsed",
            )
        else:
            choice = st.session_state[key]

        # Store response and advance
        if choice is not None and len(st.session_state.responses) == idx:
            value = options[choice]
            self.state.add_response(value)
            st.rerun()

    def display_result(self):
        st.success("✅ Survey completed.")

    def get_user_responses(self):
        return self.state.get_responses()

    def reset_survey(self):
        self.state.reset()


# ---------- CONTROLLER ----------
class FrontendController:
    """Orchestrates model and view."""

    def __init__(self, model_path="employee_attrition_dataset_text_verdict.csv"):
        self.model_controller = load_model(model_path)
        self.questions = self.model_controller.view.questions
        self.view = StreamlitSurveyView(self.questions)

    def run(self):
        finished = self.view.render()
        if finished:
            responses = self.view.get_user_responses()
            prediction = self.model_controller.model.predict(responses)
            st.markdown(f"### 🔮 Predicted Employee Verdict: **{prediction}**")
            if st.button("🔁 Start Over"):
                self.view.reset_survey()
                st.rerun()


# ---------- MAIN ----------
if __name__ == "__main__":
    controller = FrontendController()
    controller.run()
