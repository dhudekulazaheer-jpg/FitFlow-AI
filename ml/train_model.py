
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from config import PROCESSED_DIR, MODEL_DIR


# Input features
NUMERICAL_FEATURES = [
    "age",
    "weight_kg",
    "height_m",
    "experience_level",
    "workout_frequency_days_week",
    "session_duration_hours"
]

CATEGORICAL_FEATURES = [
    "gender",
    "workout_type"
]

TARGET_COLUMN = "calories_burned"


def load_data():
    print("\n1. LOADING REGRESSION DATA")
    print("-" * 45)

    X_train = pd.read_csv(
        PROCESSED_DIR / "X_train_regression.csv"
    )
    X_test = pd.read_csv(
        PROCESSED_DIR / "X_test_regression.csv"
    )

    y_train = pd.read_csv(
        PROCESSED_DIR / "y_train_regression.csv"
    ).squeeze("columns")

    y_test = pd.read_csv(
        PROCESSED_DIR / "y_test_regression.csv"
    ).squeeze("columns")

    print("Training records:", len(X_train))
    print("Testing records:", len(X_test))

    return X_train, X_test, y_train, y_test


def build_pipeline():
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES
            ),
            (
                "numerical",
                "passthrough",
                NUMERICAL_FEATURES
            )
        ]
    )

    model = RandomForestRegressor(
        n_estimators=300,
        max_depth=None,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ]
    )

    return pipeline


def evaluate_model(model, X_test, y_test, model_name):
    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    results = {
        "model": model_name,
        "MAE": round(float(mae), 2),
        "RMSE": round(float(rmse), 2),
        "R2": round(float(r2), 4)
    }

    return results, predictions


def main():
    print("=" * 55)
    print("FITFLOW AI - RANDOM FOREST REGRESSION TRAINING")
    print("=" * 55)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    X_train, X_test, y_train, y_test = load_data()

    # Train baseline model
    print("\n2. TRAINING BASELINE MODEL")
    print("-" * 45)

    baseline = DummyRegressor(strategy="mean")
    baseline.fit(X_train, y_train)

    baseline_results, _ = evaluate_model(
        baseline,
        X_test,
        y_test,
        "Mean Baseline"
    )

    print("Baseline training completed.")

    # Train Random Forest model
    print("\n3. TRAINING RANDOM FOREST REGRESSOR")
    print("-" * 45)

    model = build_pipeline()
    model.fit(X_train, y_train)

    print("Random Forest training completed.")

    # Evaluate both models
    print("\n4. MODEL EVALUATION")
    print("-" * 45)

    rf_results, predictions = evaluate_model(
        model,
        X_test,
        y_test,
        "Random Forest"
    )

    results = [baseline_results, rf_results]

    for result in results:
        print(f"\n{result['model']}")
        print("MAE :", result["MAE"])
        print("RMSE:", result["RMSE"])
        print("R2  :", result["R2"])

    # Save model
    model_path = MODEL_DIR / "calorie_regressor.pkl"
    joblib.dump(model, model_path)

    print("\n5. SAVING TRAINED MODEL")
    print("-" * 45)
    print("Model saved at:", model_path)

    # Save metrics
    metrics_path = MODEL_DIR / "regression_metrics.json"

    with open(metrics_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)

    # Save actual vs predicted values
    comparison = pd.DataFrame({
        "actual_calories": y_test.values,
        "predicted_calories": predictions
    })

    comparison.to_csv(
        PROCESSED_DIR / "regression_predictions.csv",
        index=False
    )

    print("\nEvaluation metrics saved at:", metrics_path)
    print(
        "Predictions saved at:",
        PROCESSED_DIR / "regression_predictions.csv"
    )

    # Compare model with baseline
    print("\n6. BASELINE COMPARISON")
    print("-" * 45)

    if rf_results["MAE"] < baseline_results["MAE"]:
        print("Random Forest has lower MAE than the baseline.")
    else:
        print("Random Forest did not improve MAE over the baseline.")

    print("\n" + "=" * 55)
    print("REGRESSION MODEL TRAINING COMPLETED!")
    print("=" * 55)


if __name__ == "__main__":
    main()
