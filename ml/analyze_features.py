
import pandas as pd
import joblib

from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import mutual_info_classif

from config import CLEANED_GYM_FILE, MODEL_DIR, PROCESSED_DIR


def main():
    print("=" * 50)
    print("FITFLOW AI - FEATURE ANALYSIS")
    print("=" * 50)

    # Load original dataset
    df = pd.read_csv(CLEANED_GYM_FILE)

    features = [
        "age",
        "gender",
        "bmi",
        "experience_level",
    ]

    target = "workout_type"

    X = df[features].copy()
    y = df[target].copy()

    # Load saved training and testing data
    X_test = pd.read_csv(PROCESSED_DIR / "X_test.csv")
    y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv")["workout_type"]

    model = joblib.load(MODEL_DIR / "workout_classifier.pkl")

    # 1. Target distribution
    print("\n1. WORKOUT CATEGORY DISTRIBUTION")
    print("-" * 45)
    print(y.value_counts())
    print("\nPercentage:")
    print((y.value_counts(normalize=True) * 100).round(2))

    # 2. Compare category averages
    print("\n2. FEATURE AVERAGES BY WORKOUT CATEGORY")
    print("-" * 45)

    print(
        df.groupby(target)[
            ["age", "bmi", "experience_level"]
        ].mean().round(2)
    )

    # 3. Gender distribution by category
    print("\n3. GENDER DISTRIBUTION")
    print("-" * 45)

    print(pd.crosstab(df[target], df["gender"]))

    # 4. Random Forest feature importance
    print("\n4. RANDOM FOREST FEATURE IMPORTANCE")
    print("-" * 45)

    importance = pd.DataFrame({
        "feature": X_test.columns,
        "importance": model.feature_importances_,
    })

    importance = importance.sort_values(
        by="importance",
        ascending=False,
    )

    print(importance.to_string(index=False))

    importance.to_csv(
        PROCESSED_DIR / "feature_importance.csv",
        index=False,
    )

    # 5. Mutual information
    print("\n5. MUTUAL INFORMATION ANALYSIS")
    print("-" * 45)

    X_encoded = pd.get_dummies(
        X,
        columns=["gender"],
        dtype=int,
    )

    mi_scores = mutual_info_classif(
        X_encoded,
        y,
        random_state=42,
    )

    mi_results = pd.DataFrame({
        "feature": X_encoded.columns,
        "mutual_information": mi_scores,
    }).sort_values(
        by="mutual_information",
        ascending=False,
    )

    print(mi_results.to_string(index=False))

    mi_results.to_csv(
        PROCESSED_DIR / "mutual_information.csv",
        index=False,
    )

    # 6. Majority-class baseline
    print("\n6. BASELINE COMPARISON")
    print("-" * 45)

    dummy = DummyClassifier(strategy="most_frequent")

    y_train = pd.read_csv(
        PROCESSED_DIR / "y_train.csv"
    )["workout_type"]

    dummy.fit(
        pd.read_csv(PROCESSED_DIR / "X_train.csv"),
        y_train,
    )

    baseline_predictions = dummy.predict(X_test)
    model_predictions = model.predict(X_test)

    print(
        "Majority-class baseline accuracy:",
        round(
            accuracy_score(y_test, baseline_predictions) * 100,
            2,
        ),
        "%",
    )

    print(
        "Random Forest accuracy:",
        round(
            accuracy_score(y_test, model_predictions) * 100,
            2,
        ),
        "%",
    )

    print("\nAnalysis files saved in:", PROCESSED_DIR)
    print("\nFEATURE ANALYSIS COMPLETED!")


if __name__ == "__main__":
    main()
