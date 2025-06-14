import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# synthetic data
np.random.seed(42)
data_size = 500
data = {
    'Job_Satisfaction': np.random.randint(0, 2, data_size),
    'Leadership_Perception': np.random.randint(0, 2, data_size),
    'Career_Growth': np.random.randint(0, 2, data_size),
    'Work_Life_Balance': np.random.randint(0, 2, data_size),
    'Organizational_Support': np.random.randint(0, 2, data_size),
    'Attrition': np.random.randint(0, 2, data_size)  # 0 = No Attrition, 1 = Attrition
}
df = pd.DataFrame(data)
#splitting into training and testing
X = df[['Job_Satisfaction', 'Leadership_Perception', 'Career_Growth', 'Work_Life_Balance', 'Organizational_Support']]
y = df['Attrition']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Testing model accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy:.2f}")

#predicting attrition based on input values
def predict_attrition(job_satisfaction, leadership_perception, career_growth, work_life_balance, org_support):
    input_data = np.array([[job_satisfaction, leadership_perception, career_growth, work_life_balance, org_support]])
    prediction = model.predict(input_data)[0]
    result = "Likely to Leave" if prediction == 1 else "Unlikely to Leave"
    return result

# Example Input (Replace values as needed)
job_satisfaction = int(input("Job Satisfaction (0/1): "))
leadership_perception = int(input("Leadership Perception (0/1): "))
career_growth = int(input("Career Growth (0/1): "))
work_life_balance = int(input("Work-Life Balance (0/1): "))
org_support = int(input("Organizational Support (0/1): "))

# Predict Attrition
result = predict_attrition(job_satisfaction, leadership_perception, career_growth, work_life_balance, org_support)
print(f"Prediction: {result}")

# Classification Report
# print("\nClassification Report:\n")
# print(classification_report(y_test, y_pred))
