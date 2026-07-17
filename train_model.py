import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import os

# Dataset Load
data = pd.read_csv("dataset/student_data.csv")

# Features (Input)
X = data.drop("FinalMarks", axis=1)

# Target (Output)
y = data["FinalMarks"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

# Train
model.fit(X_train, y_train)

# Create models folder if it doesn't exist
os.makedirs("models", exist_ok=True)

# Save Model
joblib.dump(model, "models/student_model.pkl")

print("====================================")
print(" AI Model Trained Successfully")
print(" Model saved in models/student_model.pkl")
print("====================================")