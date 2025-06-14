import streamlit as st
import numpy as np
from attrition_framework import AttritionController


@st.cache_resource
def load_model(model_path):
    """
    Load and initialize the AttritionController with data from the given path.
    This function is cached to avoid reloading the model on every rerun.

    Args:
        model_path (str): Path to the employee attrition dataset.

    Returns:
        AttritionController: Initialized and trained controller object.
    """
    controller = AttritionController(data_path=model_path)
    controller.model.load_and_clean_data()
    controller.model.train()
    return controller


class SurveySessionState:
    """
    Manages and persists session state for the survey using Streamlit's session_state.
    Tracks current question index and user responses.
    """

    def __init__(self, total_questions):
        """
        Initialize session state variables.

        Args:
            total_questions (int): Total number of questions in the survey.
        """
        self.total_questions = total_questions
        self._init_state()

    def _init_state(self):
        """Initialize session state variables if not already set."""
        if "current_q" not in st.session_state:
            st.session_state.current_q = 0
        if "responses" not in st.session_state:
            st.session_state.responses = []

    def get_current_question_index(self):
        """
        Get the index of the current question being displayed.

        Returns:
            int: Current question index.
        """
        return st.session_state.current_q

    def add_response(self, value):
        """
        Store a user's response and move to the next question.

        Args:
            value (int): Numerical value representing the user's answer.
        """
        st.session_state.responses.append(value)
        st.session_state.current_q += 1

    def is_complete(self):
        """
        Check if the survey has been completed.

        Returns:
            bool: True if all questions have been answered.
        """
        return st.session_state.current_q >= self.total_questions

    def get_responses(self):
        """
        Get the list of responses provided by the user.

        Returns:
            np.ndarray: 2D array of responses.
        """
        return np.array([st.session_state.responses])

    def reset(self):
        """
        Reset the survey state and clear previous responses.
        """
        st.session_state.current_q = 0
        st.session_state.responses = []
        for i in range(self.total_questions):
            st.session_state.pop(f"question_{i}", None)


class StreamlitSurveyView:
    """
    Renders the survey UI and progress bar using Streamlit.
    Manages question display and collects user input.
    """

    def __init__(self, questions):
        """
        Initialize the survey view with a list of questions.

        Args:
            questions (List[str]): List of questions to be asked.
        """
        self.questions = questions
        self.state = SurveySessionState(total_questions=len(questions))

    def render(self):
        """
        Render the current survey screen and return completion status.

        Returns:
            bool: True if survey is complete, False otherwise.
        """
        st.title("🧑‍💼 Employee Attrition Survey")

        current = self.state.get_current_question_index()
        total = self.state.total_questions
        percentage = int((current / total) * 100)

        if current >= total:
            status_label = "✅ Completed"
            percentage = 100
            display_q = total
        else:
            status_label = f"📌 Question <strong>{current + 1}</strong> of <strong>{total}</strong>"
            display_q = current + 1

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
                width: {percentage}% ;
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
        """
        Display the current survey question and collect the user's answer.
        """
        idx = self.state.get_current_question_index()
        st.subheader(f"Question {idx + 1}")
        key = f"question_{idx}"

        st.markdown(
            f"<div style='font-size: 24px; font-weight: 600; margin-bottom: 8px;'>{self.questions[idx]}</div>",
            unsafe_allow_html=True,
        )

        options = {
            "Not Satisfactory": 1,
            "Slightly Satisfactory": 2,
            "Neutral": 3,
            "Satisfactory": 4,
            "Highly Satisfied": 5,
        }

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

        if choice is not None and len(st.session_state.responses) == idx:
            value = options[choice]
            self.state.add_response(value)
            st.rerun()

    def display_result(self):
        """
        Display a success message once the survey is complete.
        """
        st.success("✅ Survey completed.")

    def get_user_responses(self):
        """
        Retrieve user responses collected during the survey.

        Returns:
            np.ndarray: 2D array of user responses.
        """
        return self.state.get_responses()

    def reset_survey(self):
        """
        Reset the survey to its initial state.
        """
        self.state.reset()


class FormController:
    """
    Controls the overall survey flow by connecting the model and UI components.
    """

    def __init__(
        self, model_path="dataset/employee_attrition_dataset_text_verdict.csv"
    ):
        """
        Initialize the controller with model and survey view.

        Args:
            model_path (str): Path to the dataset used to train the model.
        """
        self.model_controller = load_model(model_path)
        self.questions = self.model_controller.view.questions
        self.view = StreamlitSurveyView(self.questions)

    def run(self):
        """
        Run the survey view and display prediction upon completion.
        """
        finished = self.view.render()
        if finished:
            responses = self.view.get_user_responses()
            prediction = self.model_controller.model.predict(responses)
            st.markdown(f"### 🔮 Predicted Employee Verdict: **{prediction}**")
            if st.button("🔁 Start Over"):
                self.view.reset_survey()
                st.rerun()
