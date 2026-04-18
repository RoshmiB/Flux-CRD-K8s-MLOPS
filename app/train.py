import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import KFold, train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error,mean_absolute_error
from statsmodels.formula.api import ols
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
import warnings


# Suppress all warnings in the script
warnings.filterwarnings("ignore")

# Load the California housing dataset
data = fetch_california_housing()
# print(data.DESCR)
# Create a DataFrame from the dataset
df = pd.DataFrame(data.data, columns=data.feature_names)
df["PRICE"] = data.target #   Add target variable to the DataFrame
print(df.head(10))

# Get column details
print(df.info())
print(df.shape)

#check for missing values
print(df.isnull().sum())

#Statistical summary of the dataset
print(df.describe())

#visualize with KDE plot
sns.kdeplot(df['PRICE'], shade=True)
plt.title('KDE Plot of House Values')
plt.xlabel('House Value')
plt.ylabel('Density')
plt.show()

#Most houses are mid-priced,Few expensive houses → long tail,Value capped at 5.0

# Visualize the distribution of the target variable (house values)
sns.histplot(df['PRICE'], bins=30, kde=True)
plt.title('Distribution of House Values')

plt.xlabel('House Value')
plt.ylabel('Frequency')
plt.show()



# Check for outliers using boxplot
plt.figure(figsize=(10, 6))
# sns.boxplot(data=df)
sns.boxplot(x=df['PRICE'])  # Boxplot for the target variable
plt.title('Boxplot of Features')
plt.xticks(rotation=45)
plt.show()

# significant outliers in population and occupancy, which could impact model stability.

# Correlation heatmap
plt.figure(figsize=(12, 8))
sns.heatmap(df.corr(), annot=True, cmap='Blues', fmt='.2f')
plt.title('Correlation Heatmap')
plt.show()

#Median income showed the strongest correlation with house price, making it a key predictive feature

#show pairplot to visualize relationships between features and target variable
sns.pairplot(df, x_vars=data.feature_names, y_vars='PRICE', height=2.5)
plt.suptitle('Pairplot of Features vs. House Values', y=1.02)
plt.show()

# The pairplot reveals positive correlations between median income and house values, while features like latitude and longitude show more complex relationships, indicating the importance of location in housing prices.

# Based on the EDA, we can conclude that median income is a strong predictor of house values, and there are significant outliers in population and occupancy that may need to be addressed during model training. The distribution of house values is right-skewed, suggesting that transformations may be necessary for better model performance.
# Next steps would involve data preprocessing, feature engineering, and model training to predict house values based on the identified relationships.

#Remove highly correlated features to reduce multicollinearity
df.drop([ 'AveBedrms'], axis=1, inplace=True)
# df.drop(['Latitude'],axis=1,inplace=True)

#Remove outliers in population and occupancy using IQR method
Q1 = df[['Population', 'AveOccup']].quantile(0.25)
Q3 = df[['Population', 'AveOccup']].quantile(0.75)
IQR = Q3 - Q1
filter = (df[['Population', 'AveOccup']] >= (Q1 - 1.5 * IQR)) & (df[['Population', 'AveOccup']] <= (Q3 + 1.5 * IQR))
# df = df[filter.all(axis=1)]

# Create new features based on existing ones to capture more complex relationships
df['rooms_per_household'] = df['AveRooms'] / df['AveOccup']
# df['bedrooms_per_room'] = df['AveBedrms'] / df['AveRooms']

# Apply log transformation to the target variable to address skewness
# df['PRICE'] = np.log1p(df['PRICE'])

# Visualize the distribution of the transformed target variable
sns.histplot(df['PRICE'], bins=30, kde=True)
plt.title('Distribution of Transformed House Values')
plt.xlabel('Transformed House Value')
plt.ylabel('Frequency')
plt.show()

# Check the columns of the data to identify the features and target variable
print(df.columns)

# Select features and target variable for regression
features = df.drop('PRICE', axis=1)  # All columns except 'PRICE' are features
target = df['PRICE']  # 'PRICE' is the target variable

X= features
y= target

print(X.columns)

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Check the data
print("Training Features:")
print(X_train[:5]) # Check the first 5 rows of the training features


# Standardize the features
# Initialize a scaler
scaler = StandardScaler()

# Scale the train and test data
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Check the data
print("Scaled Training Features:")
print(X_train_scaled[:5])

# Train a linear regression model
model1 = LinearRegression()
model1.fit(X_train_scaled, y_train)
print(model1.score(X_test_scaled, y_test)) 
# R^2 score of the linear regression model = 0.6733284290139305




# After baseline linear regression, we sould try tree-based models like Random Forest or 
# Gradient Boosting to handle non-linearity and outliers better, and also consider hyperparameter tuning and cross-validation to optimize model performance.
# Random Forest Regressor do not require feature scaling and can handle non-linear relationships and outliers better than linear regression, making it a good choice for improving model performance on this dataset.

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
print(model2.get_params())

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

# The best hyperparameters found through GridSearchCV resulted in the highest R^2 score of approximately 0.81 on the validation set, 
# indicating that this configuration provides the best balance of model complexity and performance for predicting house values in the California housing dataset.

#check cross-validation scores for the best model
kf = KFold(n_splits=5, shuffle=True, random_state=42) 
scores = cross_val_score(
    best_model,
    X,
    y,
    cv=kf,
    scoring="r2"
)

print("CV Scores:", scores)
print("Average CV Score:", scores.mean())

#The cross-validation scores for the best Random Forest model are [0.80627287 0.81394161 0.80621886 0.82409708 0.80646526], with an average R^2 score of approximately 0.811, indicating that the model performs consistently well across different subsets of the data, suggesting good generalization to unseen data.

## Previously
## The cross-validation scores for the best Random Forest model are [0.45, 0.71, 0.73, 0.61, 0.68], 
## with an average R^2 score of approximately 0.636, indicating that while the model performs well on the training data, 
## there is some variability in its performance across different subsets of the data, 
## suggesting potential overfitting or sensitivity to certain data splits.


# Model Building using statsmodels library
# Add the intercept term
X = sm.add_constant(X)
# Splitting the data in 70:30 ratio of train to test data
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30 , random_state = 1)
# Create the model
model3 = sm.OLS(y_train, X_train_scaled).fit()
# Get the model summary
print(model3.summary())

#R-squared (uncentered):                   0.159
#[1] R² is computed without centering (uncentered) since the model does not contain a constant.
#[2] Standard Errors assume that the covariance matrix of the errors is correctly specified.


#Model Building using GradientBoostingRegressor
gbr = GradientBoostingRegressor()
gbr.fit(X_train, y_train)

y_pred = gbr.predict(X_test)

print("GBR R2:", r2_score(y_test, y_pred))


# save best model
model_data = {
    "model": grid.best_estimator_, # best model from GridSearchCV
    "features": list(X.columns)
}
import pickle
pickle.dump(model_data, open("model.pkl", "wb"))
print("Model saved as model.pkl")


