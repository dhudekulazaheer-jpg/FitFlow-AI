
import json
import joblib
import pandas as pd

from config import MODEL_DIR, PROCESSED_DIR


def load_model():
    model_path = MODEL_DIR / "calorie_regressor.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Trained model not found: {model_path}"
        )

    return joblib.load(model_path)


def analyze_feature_importance(model):
    print("\n1. FEATURE IMPORTANCE ANALYSIS")
    print("-" * 50)

    preprocessor = model.named_steps["preprocessor"]
    regressor = model.named_steps["regressor"]

    feature_names = preprocessor.get_feature_names_out()
    importance_values = regressor.feature_importances_

    importance_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importance_values
    })

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False
    ).reset_index(drop=True)

    importance_df["importance_percentage"] = (
        importance_df["importance"] * 100
    ).round(2)

    print(importance_df.to_string(index=False))

    output_path = (
        PROCESSED_DIR / "feature_importance.csv"
    )

    importance_df.to_csv(output_path, index=False)

    print("\nFeature importance report saved at:")
    print(output_path)

    return importance_df


def analyze_prediction_errors():
    print("\n2. PREDICTION ERROR ANALYSIS")
    print("-" * 50)

    prediction_path = (
        PROCESSED_DIR / "regression_predictions.csv"
    )

    if not prediction_path.exists():
        raise FileNotFoundError(
            f"Prediction file not found: {prediction_path}"
        )

    df = pd.read_csv(prediction_path)

    df["absolute_error"] = (
        df["actual_calories"] -
        df["predicted_calories"]
    ).abs()

    print("\nPrediction summary:")
    print(
        df[
            [
                "actual_calories",
                "predicted_calories",
                "absolute_error"
            ]
        ].describe().round(2)
    )

    print("\nAverage absolute error:")
    print(round(df["absolute_error"].mean(), 2))

    print("\nLargest prediction errors:")
    print(
        df.nlargest(10, "absolute_error")[
            [
                "actual_calories",
                "predicted_calories",
                "absolute_error"
            ]
        ].round(2).to_string(index=False)
    )

    error_path = (
        PROCESSED_DIR / "prediction_error_analysis.csv"
    )

    df.to_csv(error_path, index=False)

    print("\nError analysis saved at:")
    print(error_path)


def display_model_metrics():
    print("\n3. MODEL PERFORMANCE SUMMARY")
    print("-" * 50)

    metrics_path = MODEL_DIR / "regression_metrics.json"

    with open(metrics_path, "r", encoding="utf-8") as file:
        metrics = json.load(file)

    for result in metrics:
        print(f"\n{result['model']}")
        print("MAE :", result["MAE"])
        print("RMSE:", result["RMSE"])
        print("R2  :", result["R2"])


def main():
    print("=" * 55)
    print("FITFLOW AI - MODEL ANALYSIS")
    print("=" * 55)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    model = load_model()

    analyze_feature_importance(model)
    analyze_prediction_errors()
    display_model_metrics()

    print("\n" + "=" * 55)
    print("MODEL ANALYSIS COMPLETED!")
    print("=" * 55)


if __name__ == "__main__":
    main()

