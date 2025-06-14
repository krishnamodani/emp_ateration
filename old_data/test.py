# import numpy as np
# import pandas as pd
# from abc import ABC, abstractmethod
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score
# import warnings

# warnings.filterwarnings("ignore")

# # ================================
# # STRATEGY PATTERN (Model Strategy)
# # ================================

# class ModelStrategy(ABC):
#     """
#     Interface for machine learning model strategies.
#     Provides abstract methods for training and prediction.
#     """

#     @abstractmethod
#     def train(self, X_train, y_train):
#         """
#         Trains the ML model on the provided training data.

#         Parameters:
#         - X_train: Features for training.
#         - y_train: Target values for training.
#         """
#         pass

#     @abstractmethod
#     def predict(self, input_data):
#         """
#         Makes predictions using the trained model.

#         Parameters:
#         - input_data: Features to make predictions on.

#         Returns:
#         - Predicted labels or values.
#         """
#         pass


# class RandomForestStrategy(ModelStrategy):
#     """
#     Strategy class for RandomForestClassifier from scikit-learn.
#     """

#     def __init__(self):
#         self.model = RandomForestClassifier(n_estimators=100, random_state=42)

#     def train(self, X_train, y_train):
#         self.model.fit(X_train, y_train)

#     def predict(self, input_data):
#         return self.model.predict(input_data)


# # =====================
# # FACTORY PATTERN
# # =====================

# class ModelFactory:
#     """
#     Factory class to instantiate model strategies based on a given name.
#     """

#     @staticmethod
#     def get_model(name: str) -> ModelStrategy:
#         """
#         Returns a model strategy object for the given name.

#         Parameters:
#         - name: Name of the ML strategy (e.g., "randomforest")

#         Returns:
#         - ModelStrategy instance
#         """
#         if name.lower() == "randomforest":
#             return RandomForestStrategy()
#         else:
#             raise ValueError(f"❌ Model '{name}' is not implemented yet.")


# # ===============================
# # MODEL CLASS (Data & Processing)
# # ===============================

# class AttritionModel:
#     """
#     Handles data processing, training, and prediction for the attrition model.
#     """

#     def __init__(self, data_path: str, model_strategy: ModelStrategy):
#         self.data_path = data_path
#         self.model_strategy = model_strategy
#         self.df = None

#         # Mapping for textual to numeric verdicts
#         self.verdict_map = {
#             'Will Leave': 1,
#             'Likely To Leave': 2,
#             'Not Decided': 3,
#             'Less Likely To Leave': 4,
#             'Wont Leave': 5
#         }
#         self.reverse_verdict_map = {v: k for k, v in self.verdict_map.items()}

#     def load_and_clean_data(self):
#         """
#         Loads and cleans the dataset from the given CSV file.
#         Converts textual verdicts into numeric format.
#         """
#         self.df = pd.read_csv(self.data_path)

#         self.df['Final_Verdict'] = (
#             self.df['Final_Verdict']
#             .astype(str)
#             .str.strip()
#             .str.title()
#         )

#         self.df['Final_Verdict_Num'] = self.df['Final_Verdict'].map(self.verdict_map)

#         if self.df['Final_Verdict_Num'].isna().any():
#             print("❌ Unmapped verdict values found:")
#             print(self.df[self.df['Final_Verdict_Num'].isna()]['Final_Verdict'].value_counts())
#             raise ValueError("Please fix or remove unmapped verdict values.")

#         self.df.dropna(inplace=True)

#     def train(self):
#         """
#         Trains the model using the given strategy.
#         Splits the data, fits the model, and prints accuracy.
#         """
#         X = self.df.drop(columns=['Final_Verdict', 'Final_Verdict_Num'])
#         y = self.df['Final_Verdict_Num']

#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=0.2, random_state=42, stratify=y
#         )

#         self.model_strategy.train(X_train, y_train)

#         y_pred = self.model_strategy.predict(X_test)
#         accuracy = accuracy_score(y_test, y_pred)

#         print(f"\n📊 Model Accuracy: {accuracy:.2f}")

#     def predict(self, input_array):
#         """
#         Predicts the final verdict based on new survey responses.

#         Parameters:
#         - input_array: A 2D NumPy array of survey responses (1 row)

#         Returns:
#         - Predicted verdict (textual)
#         """
#         pred_num = self.model_strategy.predict(input_array)[0]
#         return self.reverse_verdict_map.get(pred_num, "Unknown")


# # =======================
# # VIEW (User Survey Input)
# # =======================

# class SurveyView:
#     """
#     Responsible for displaying survey questions and collecting responses.
#     """

#     def __init__(self):
#         self.questions = [
#             "I feel satisfied with the work I do on a daily basis.",
#             "I feel motivated to do my best at work every day.",
#             "My current role aligns well with my skills and interests.",
#             "I feel recognized and appreciated for my contributions.",
#             "I have adequate opportunities for growth and advancement in this organization.",
#             "I receive regular feedback that helps me improve my performance.",
#             "I believe my career goals can be achieved in this organization.",
#             "I feel respected and valued by my coworkers.",
#             "The work environment here promotes collaboration and inclusion.",
#             "I feel like I belong in this organization.",
#             "My manager supports me in my professional development.",
#             "I trust the leadership of this organization.",
#             "Management communicates openly and transparently.",
#             "I am able to maintain a healthy work-life balance.",
#             "I feel mentally and physically well at work.",
#             "My workload is manageable and fair.",
#             "I see myself working here in the next 12 months.",
#             "I rarely think about looking for a job elsewhere.",
#             "If offered a similar role elsewhere, I would still prefer to stay here.",
#             "Overall, I am satisfied with my experience in this organization."
#         ]

#     def collect_responses(self):
#         """
#         Prompts the user for responses to each survey question.

#         Returns:
#         - A 2D NumPy array containing the 20 responses (shape: 1 x 20)
#         """
#         print("\n📋 Please answer the following 20 questions on a scale of 1 (lowest) to 5 (highest):")
#         responses = []

#         for i, question in enumerate(self.questions, 1):
#             while True:
#                 try:
#                     value = int(input(f"{i}. {question} (1-5): "))
#                     if 1 <= value <= 5:
#                         responses.append(value)
#                         break
#                     else:
#                         raise ValueError
#                 except ValueError:
#                     print("❌ Invalid input. Please enter a number between 1 and 5.")

#         return np.array([responses])


# # ====================
# # CONTROLLER (Main App)
# # ====================

# class AttritionController:
#     """
#     Coordinates the model, view, and user input to complete the attrition prediction workflow.
#     """

#     def __init__(self, data_path: str, model_type: str = "randomforest"):
#         """
#         Initializes the controller with dataset path and model type.

#         Parameters:
#         - data_path: Path to the CSV file containing employee survey data.
#         - model_type: Name of the model strategy to use.
#         """
#         strategy = ModelFactory.get_model(model_type)
#         self.model = AttritionModel(data_path, strategy)
#         self.view = SurveyView()

#     def run(self):
#         """
#         Executes the full application pipeline:
#         - Loads and cleans the data
#         - Trains the model
#         - Collects new responses
#         - Predicts and prints the result
#         """
#         self.model.load_and_clean_data()
#         self.model.train()
#         responses = self.view.collect_responses()
#         prediction = self.model.predict(responses)
#         print(f"\n🔮 Predicted Employee Verdict: {prediction}")


# # ====================
# # ENTRY POINT
# # ====================
# if __name__ == "__main__":
#     # Modify the path if your CSV is located elsewhere
#     controller = AttritionController(data_path="dataset/employee_attrition_dataset_text_verdict.csv")
#     controller.run()
