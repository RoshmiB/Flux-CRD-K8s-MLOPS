import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import  train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import  RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error,mean_absolute_error
import warnings
import pickle

# Suppress all warnings in the script
warnings.filterwarnings("ignore")

# Load the California housing dataset
data = fetch_california_housing()
# print(data.DESCR)
# Create a DataFrame from the dataset
df = pd.DataFrame(data.data, columns=data.feature_names)
df["PRICE"] = data.target #   Add target variable to the DataFrame
print(df.head(10))

#Remove highly correlated features to reduce multicollinearity
df.drop([ 'AveBedrms'], axis=1, inplace=True)
# Create new features based on existing ones to capture more complex relationships
df['rooms_per_household'] = df['AveRooms'] / df['AveOccup']


# Select features and target variable for regression
features = df.drop('PRICE', axis=1)  # All columns except 'PRICE' are features
target = df['PRICE']  # 'PRICE' is the target variable
X= features
y= target
print(X.columns)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the Random Forest Regressor
model2 = RandomForestRegressor(n_estimators=100, random_state=42)
# Train the model on the training data
model2.fit(X_train, y_train)
# Predict on the test data
y_pred = model2.predict(X_test)
# Evaluate the model performance
mean_squared_error = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
mean_absolute_error = mean_absolute_error(y_test, y_pred)


print(f"Random Forest Regressor Performance:")
print(f"Mean Squared Error: {mean_squared_error}") # 0.257026012624009
print(f"R^2 Score: {r2}") # 0.8129416461881585
print(f"Mean Absolute Error: {mean_absolute_error}") # 0.32977143419166466


# Check Hyperparameters of the Random Forest model
param_grid = {
    "n_estimators": [50, 100],
    "max_depth": [10, 20, None],
    "min_samples_split": [2, 5]
}

grid = GridSearchCV(
    model2,
    param_grid,
    cv=3
)
grid.fit(X_train, y_train)

# Evaluate
best_model = grid.best_estimator_
y_pred = best_model.predict(X_test)
print("R2:", r2_score(y_test, y_pred))

# save best model
model_data = {
    "model": grid.best_estimator_, # best model from GridSearchCV
    "features": list(X.columns)
}

pickle.dump(model_data, open("model.pkl", "wb"))
print("Model saved as model.pkl")