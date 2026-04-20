import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
import pickle

warnings.filterwarnings("ignore")

# Load dataset
data = fetch_california_housing()
df = pd.DataFrame(data.data, columns=data.feature_names)
df["PRICE"] = data.target

# -------------------------------
# STEP 1: Split BEFORE EDA
# -------------------------------
X = df.drop("PRICE", axis=1)
y = df["PRICE"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -------------------------------
# STEP 2: EDA / Feature Engineering (apply SAME logic to both)
# -------------------------------
def preprocess(df):
    df = df.copy()
    
    # Drop correlated feature
    df = df.drop(['AveBedrms'], axis=1)
    
    # Feature engineering
    df['rooms_per_household'] = df['AveRooms'] / df['AveOccup']
    
    return df

X_train = preprocess(X_train)
X_test = preprocess(X_test)

print("Features used:", X_train.columns)

# -------------------------------
# STEP 3: Train baseline model
# -------------------------------
model = RandomForestRegressor(random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("\nBaseline Model Performance:")
print("MSE:", mean_squared_error(y_test, y_pred))
print("R2:", r2_score(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))

# -------------------------------
# STEP 4: Randomized Search (instead of GridSearch)
# -------------------------------
param_dist = {
    "n_estimators": [50, 100, 200, 300],
    "max_depth": [10, 20, 30, None],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2", None]
}

random_search = RandomizedSearchCV(
    estimator=RandomForestRegressor(random_state=42),
    param_distributions=param_dist,
    n_iter=20,              # number of random combinations
    cv=3,
    verbose=1,
    random_state=42,
    n_jobs=-1
)

random_search.fit(X_train, y_train)

# -------------------------------
# STEP 5: Evaluate best model
# -------------------------------
best_model = random_search.best_estimator_
y_pred = best_model.predict(X_test)

print("\nTuned Model Performance:")
print("Best Params:", random_search.best_params_)
print("R2:", r2_score(y_test, y_pred))
print("MSE:", mean_squared_error(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))

# -------------------------------
# STEP 6: Save model
# -------------------------------
model_data = {
    "model": best_model,
    "features": list(X_train.columns)
}

with open("model.pkl", "wb") as f:   # meaning open for writing in binary mode
    pickle.dump(model_data, f)

print("\nModel saved as model.pkl")