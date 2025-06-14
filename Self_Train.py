import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

# Step 1: Take Custom Inputs Directly from User
n = int(input("Enter the number of employee records: "))

data = []
for i in range(n):
    print(f"\nEnter details for Employee {i + 1}:")
    job_satisfaction = int(input("Job Satisfaction (0/1): "))
    leadership_perception = int(input("Leadership Perception (0/1): "))
    career_growth = int(input("Career Growth (0/1): "))
    work_life_balance = int(input("Work-Life Balance (0/1): "))
    org_support = int(input("Organizational Support (0/1): "))
    attrition = int(input("Attrition (0 = No, 1 = Yes): "))
    
    data.append([job_satisfaction, leadership_perception, career_growth, work_life_balance, org_support, attrition])

# Step 2: Create DataFrame from Custom Input
df = pd.DataFrame(data, columns=['Job_Satisfaction', 'Leadership_Perception', 'Career_Growth', 
                                 'Work_Life_Balance', 'Organizational_Support', 'Attrition'])

# Step 3: Split Data into Training and Test Sets
X = df[['Job_Satisfaction', 'Leadership_Perception', 'Career_Growth', 'Work_Life_Balance', 'Organizational_Support']]
y = df['Attrition']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 4: Train Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Step 5: Predict on Test Data
y_pred = model.predict(X_test)

# Step 6: Calculate Accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.2f}")

# Step 7: Generate Classification Report
print("\nClassification Report:\n")
print(classification_report(y_test, y_pred))

# Step 8: Predict for New Employee
print("\n--- Predict Attrition for New Employee ---")
job_satisfaction = int(input("Job Satisfaction (0/1): "))
leadership_perception = int(input("Leadership Perception (0/1): "))
career_growth = int(input("Career Growth (0/1): "))
work_life_balance = int(input("Work-Life Balance (0/1): "))
org_support = int(input("Organizational Support (0/1): "))

input_data = np.array([[job_satisfaction, leadership_perception, career_growth, work_life_balance, org_support]])
prediction = model.predict(input_data)[0]
result = "Likely to Leave" if prediction == 1 else "Unlikely to Leave"
print(f"\nPrediction: {result}")
