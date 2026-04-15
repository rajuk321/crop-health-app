import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Load dataset
data = pd.read_csv("dataset/yield_data.csv")

print(data.shape)
print(data.head())

# Convert categorical → numeric
data = pd.get_dummies(data)

# Features & target
X = data.drop("yield", axis=1)
y = data["yield"]

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model
model = RandomForestRegressor()
model.fit(X_train, y_train)

# Save model
pickle.dump(model, open("models/yield_model.pkl", "wb"))

# Save columns (VERY IMPORTANT 🔥)
pickle.dump(X.columns, open("models/columns.pkl", "wb"))

# Accuracy
print("Accuracy:", model.score(X_test, y_test))