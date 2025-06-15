import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings

warnings.filterwarnings("ignore")

# ================================
# STRATEGY PATTERN (Model Strategy)
# ================================

class ModelStrategy(ABC):
    @abstractmethod
    def train(self, X_train, y_train):
        pass

    @abstractmethod
    def predict(self, input_data):
        pass

class RandomForestStrategy(ModelStrategy):
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, input_data):
        return self.model.predict(input_data)

# =====================
# FACTORY PATTERN
# =====================

class ModelFactory:
    @staticmethod
    def get_model(name: str) -> ModelStrategy:
        if name.lower() == "randomforest":
            return RandomForestStrategy()
        else:
            raise ValueError(f"❌ Model '{name}' is not implemented yet.")

# ===============================
# MODEL CLASS (Data & Processing)
# ===============================

class AttritionModel:
    def __init__(self, data_path: str, model_strategy: ModelStrategy):
        self.data_path = data_path
        self.model_strategy = model_strategy
        self.df = None

        self.verdict_map = {
            "Will Leave": 1,
            "Likely To Leave": 2,
            "Not Decided": 3,
            "Less Likely To Leave": 4,
            "Wont Leave": 5,
        }
        self.reverse_verdict_map = {v: k for k, v in self.verdict_map.items()}

    def load_and_clean_data(self):
        self.df = pd.read_csv(self.data_path)

        self.df["Final_Verdict"] = (
            self.df["Final_Verdict"].astype(str).str.strip().str.title()
        )

        self.df["Final_Verdict_Num"] = self.df["Final_Verdict"].map(self.verdict_map)

        if self.df["Final_Verdict_Num"].isna().any():
            print("❌ Unmapped verdict values found:")
            print(
                self.df[self.df["Final_Verdict_Num"].isna()][
                    "Final_Verdict"
                ].value_counts()
            )
            raise ValueError("Please fix or remove unmapped verdict values.")

        self.df.dropna(inplace=True)

    def train(self):
        X = self.df.drop(columns=["Final_Verdict", "Final_Verdict_Num", "emp_id"], errors="ignore")
        y = self.df["Final_Verdict_Num"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.model_strategy.train(X_train, y_train)

        y_pred = self.model_strategy.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)

        print(f"\n📊 Model Accuracy: {accuracy:.2f}")

    def predict_numeric(self, input_array):
        return int(self.model_strategy.predict(input_array)[0])

    def predict_textual(self, input_array):
        pred_num = self.predict_numeric(input_array)
        return self.reverse_verdict_map.get(pred_num, "Unknown")

    def get_column_names(self):
        return self.df.drop(columns=["Final_Verdict", "Final_Verdict_Num", "emp_id"], errors="ignore").columns.tolist()

# ==============================
# FACADE CONTROLLER
# ==============================

class AttritionController:
    def __init__(self, csv_path="dataset/survey_inputs.csv", model_name="randomforest"):
        strategy = ModelFactory.get_model(model_name)
        self.model = AttritionModel(data_path=csv_path, model_strategy=strategy)
        self.model.load_and_clean_data()
        self.model.train()

    def predict_from_dict(self, input_dict):
        columns = self.model.get_column_names()
        input_array = np.array([[input_dict[col] for col in columns]])
        return self.model.predict_textual(input_array)

    def get_features(self):
        return self.model.get_column_names()
