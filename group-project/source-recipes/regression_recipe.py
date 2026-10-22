# Source: https://colab.research.google.com/drive/1NQ3c6PBRBilQNopDNJ7JzWpgSZWqwk4u
# Selected original code cells; see PROVENANCE.md.

# Original cell 2
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Original cell 6
selected_features = [
    "study_hours_per_week",
    "attendance_rate_pct",
    "previous_gpa",
    "sleep_hours_per_night",
    "extracurricular_activities_count",
    "stress_level_score",
    "tutoring_hours_per_week",
    "internet_access_quality",
    "study_group_participation",
    "parental_education_level"
]

X = df[selected_features]
y = df["final_exam_score"]

print("Number of selected features:", X.shape[1])
print(selected_features)


# Original cell 8
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training set:", X_train.shape)
print("Testing set:", X_test.shape)


# Original cell 10
categorical_features = [
    "internet_access_quality",
    "study_group_participation",
    "parental_education_level"
]

numeric_features = [
    "study_hours_per_week",
    "attendance_rate_pct",
    "previous_gpa",
    "sleep_hours_per_night",
    "extracurricular_activities_count",
    "stress_level_score",
    "tutoring_hours_per_week"
]

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(
        handle_unknown="ignore",
        sparse_output=False
    ))
])

preprocessor = ColumnTransformer([
    ("numerical", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features)
])


# Original cell 12
baseline_model = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LinearRegression())
])

baseline_model.fit(X_train, y_train)
baseline_pred = baseline_model.predict(X_test)

baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))
baseline_mae = mean_absolute_error(y_test, baseline_pred)
baseline_r2 = r2_score(y_test, baseline_pred)

print("UNTUNED LINEAR REGRESSION")
print(f"RMSE: {baseline_rmse:.4f}")
print(f"MAE : {baseline_mae:.4f}")
print(f"RÂ²  : {baseline_r2:.4f}")


# Original cell 14
tuning_pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", LinearRegression())
])

param_grid = {
    "model__fit_intercept": [True, False],
    "model__positive": [False, True]
}

cv = KFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

grid_search = GridSearchCV(
    estimator=tuning_pipeline,
    param_grid=param_grid,
    scoring="neg_root_mean_squared_error",
    cv=cv,
    n_jobs=1,
    return_train_score=True
)

grid_search.fit(X_train, y_train)

print("Best parameters:", grid_search.best_params_)
print(f"Best CV RMSE: {-grid_search.best_score_:.4f}")


# Original cell 18
tuned_model = grid_search.best_estimator_

tuned_pred = tuned_model.predict(X_test)

tuned_rmse = np.sqrt(mean_squared_error(y_test, tuned_pred))
tuned_mae = mean_absolute_error(y_test, tuned_pred)
tuned_r2 = r2_score(y_test, tuned_pred)

print("TUNED LINEAR REGRESSION")
print(f"RMSE: {tuned_rmse:.4f}")
print(f"MAE : {tuned_mae:.4f}")
print(f"RÂ²  : {tuned_r2:.4f}")
