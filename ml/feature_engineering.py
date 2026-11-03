
import pandas as pd

from sklearn.model_selection import train_test_split

from config import CLEANED_GYM_FILE, PROCESSED_DIR


FEATURE_COLUMNS = [
    "age",
    "gender",
    "weight_kg",
    "height_m",
    "experience_level",
    "workout_frequency_days_week",
    "session_duration_hours",
    "workout_type",
]

TARGET_COLUMN = "calories_burned"


def load_dataset():
    if not CLEANED_GYM_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {CLEANED_GYM_FILE}"
        )

    return pd.read_csv(CLEANED_GYM_FILE)


def validate_dataset(df):
    print("\n1. DATASET VALIDATION")
    print("-" * 45)

    required = FEATURE_COLUMNS + [TARGET_COLUMN]

    missing_columns = [
        col for col in required if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    selected = df[required].copy()

    print("Total records:", len(selected))
    print("\nMissing values:")
    print(selected.isnull().sum())

    if selected.isnull().any().any():
        raise ValueError("Missing values found.")

    if (selected[TARGET_COLUMN] <= 0).any():
        raise ValueError("Invalid calorie target values found.")

    if not selected["age"].between(18, 100).all():
        raise ValueError("Invalid age values found.")

    if (selected["weight_kg"] <= 0).any():
        raise ValueError("Invalid weight values found.")

    if (selected["height_m"] <= 0).any():
        raise ValueError("Invalid height values found.")

    if not selected["experience_level"].isin([1, 2, 3]).all():
        raise ValueError("Invalid experience levels found.")

    if not selected["session_duration_hours"].gt(0).all():
        raise ValueError("Invalid session durations found.")

    if not selected["workout_frequency_days_week"].between(1, 7).all():
        raise ValueError("Invalid workout frequencies found.")

    print("\nAll selected features passed validation.")

    return selected


def prepare_features(df):
    print("\n2. PREPARING REGRESSION FEATURES")
    print("-" * 45)

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()

    print("Input features:", FEATURE_COLUMNS)
    print("Target:", TARGET_COLUMN)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
    )

    return X_train, X_test, y_train, y_test


def save_processed_data(X_train, X_test, y_train, y_test):
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    X_train.to_csv(
        PROCESSED_DIR / "X_train_regression.csv",
        index=False,
    )

    X_test.to_csv(
        PROCESSED_DIR / "X_test_regression.csv",
        index=False,
    )

    y_train.to_csv(
        PROCESSED_DIR / "y_train_regression.csv",
        index=False,
        header=True,
    )

    y_test.to_csv(
        PROCESSED_DIR / "y_test_regression.csv",
        index=False,
        header=True,
    )

    print("\n3. SAVING PROCESSED DATA")
    print("-" * 45)
    print("Regression datasets saved in:", PROCESSED_DIR)


def main():
    print("=" * 50)
    print("FITFLOW AI - REGRESSION FEATURE ENGINEERING")
    print("=" * 50)

    df = load_dataset()

    selected_df = validate_dataset(df)

    X_train, X_test, y_train, y_test = prepare_features(
        selected_df
    )

    save_processed_data(
        X_train,
        X_test,
        y_train,
        y_test,
    )

    print("\n4. DATASET SPLIT SUMMARY")
    print("-" * 45)

    print("Training records:", len(X_train))
    print("Testing records:", len(X_test))

    print("\nTraining target statistics:")
    print(y_train.describe().round(2))

    print("\nTesting target statistics:")
    print(y_test.describe().round(2))

    print("\nREGRESSION FEATURE ENGINEERING COMPLETED!")


if __name__ == "__main__":
    main()
