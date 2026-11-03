
import pandas as pd

from config import CLEANED_GYM_FILE, PROCESSED_DIR


def load_dataset():
    if not CLEANED_GYM_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {CLEANED_GYM_FILE}"
        )

    return pd.read_csv(CLEANED_GYM_FILE)


def inspect_dataset(df):
    print("\n1. DATASET OVERVIEW")
    print("-" * 50)

    print("Total records:", len(df))
    print("Total columns:", len(df.columns))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate records:", df.duplicated().sum())


def analyze_calories(df):
    print("\n2. CALORIES BURNED DISTRIBUTION")
    print("-" * 50)

    print(df["calories_burned"].describe().round(2))

    print("\nCalories burned by workout category:")

    category_stats = df.groupby("workout_type")[
        "calories_burned"
    ].agg(
        ["count", "mean", "median", "min", "max", "std"]
    ).round(2)

    print(category_stats)

    category_stats.to_csv(
        PROCESSED_DIR / "calories_by_workout_type.csv"
    )


def analyze_numerical_relationships(df):
    print("\n3. NUMERICAL FEATURE CORRELATIONS")
    print("-" * 50)

    numerical_columns = df.select_dtypes(
        include=["number"]
    ).columns

    correlation = df[numerical_columns].corr()

    calorie_correlation = (
        correlation["calories_burned"]
        .drop("calories_burned")
        .sort_values(ascending=False)
    )

    print("\nCorrelation with calories burned:")
    print(calorie_correlation.round(4))

    correlation.to_csv(
        PROCESSED_DIR / "regression_correlation_matrix.csv"
    )


def analyze_candidate_features(df):
    print("\n4. POTENTIAL MODEL INPUT FEATURES")
    print("-" * 50)

    candidate_features = [
        "age",
        "weight_kg",
        "height_m",
        "bmi",
        "experience_level",
        "session_duration_hours",
        "workout_frequency_days_week",
        "gender",
        "workout_type",
    ]

    available_features = [
        column for column in candidate_features
        if column in df.columns
    ]

    print("Candidate features:", available_features)

    print("\nNumerical feature summary:")

    numerical_features = [
        column for column in available_features
        if pd.api.types.is_numeric_dtype(df[column])
    ]

    print(df[numerical_features].describe().round(2))

    print("\nCategorical feature values:")

    for column in ["gender", "workout_type"]:
        if column in available_features:
            print(f"\n{column}:")
            print(df[column].value_counts())


def inspect_possible_leakage(df):
    print("\n5. FEATURES REQUIRING SPECIAL ATTENTION")
    print("-" * 50)

    special_features = [
        "avg_bpm",
        "max_bpm",
        "resting_bpm",
        "calories_burned",
        "fat_percentage",
        "water_intake_liters",
    ]

    for column in special_features:
        if column in df.columns:
            print(
                f"{column}: "
                f"min={df[column].min()}, "
                f"max={df[column].max()}"
            )

    print(
        "\nNote: Measurements collected during or after a workout "
        "should not automatically be used to predict calories "
        "before a workout."
    )


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 55)
    print("FITFLOW AI - REGRESSION DATA ANALYSIS")
    print("=" * 55)

    df = load_dataset()

    inspect_dataset(df)
    analyze_calories(df)
    analyze_numerical_relationships(df)
    analyze_candidate_features(df)
    inspect_possible_leakage(df)

    print("\n" + "=" * 55)
    print("REGRESSION DATA ANALYSIS COMPLETED!")
    print("Reports saved in:", PROCESSED_DIR)
    print("=" * 55)


if __name__ == "__main__":
    main()
