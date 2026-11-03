
import pandas as pd

from config import (
    CLEANED_YOGA_FILE,
    CLEANED_WORKOUT_FILE,
    CLEANED_GYM_FILE,
)


def inspect_dataset(name, file_path):
    print("\n" + "=" * 65)
    print(f"DATASET: {name}")
    print("=" * 65)

    df = pd.read_csv(file_path)

    print(f"\nTotal records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\nCOLUMN NAMES:")
    print(df.columns.tolist())

    print("\nDATA TYPES:")
    print(df.dtypes.to_string())

    print("\nMISSING VALUES:")
    print(df.isnull().sum().to_string())

    print("\nUNIQUE VALUES IN IMPORTANT COLUMNS:")

    for column in df.select_dtypes(
        include=["object", "category"]
    ).columns:

        unique_values = df[column].dropna().unique()

        print(f"\n{column}:")
        print(f"Unique count: {len(unique_values)}")
        print("Examples:", unique_values[:10].tolist())

    print("\nFIRST 3 RECORDS:")
    print(df.head(3).to_string(index=False))

    print("\nNUMERICAL DATA SUMMARY:")
    numerical_columns = df.select_dtypes(
        include=["number"]
    )

    if not numerical_columns.empty:
        print(numerical_columns.describe().round(2).to_string())
    else:
        print("No numerical columns found.")

    return df


def main():
    yoga_df = inspect_dataset(
        "YOGA DATASET",
        CLEANED_YOGA_FILE
    )

    workout_df = inspect_dataset(
        "WORKOUT DATASET",
        CLEANED_WORKOUT_FILE
    )

    gym_df = inspect_dataset(
        "GYM MEMBERS DATASET",
        CLEANED_GYM_FILE
    )

    print("\n" + "=" * 65)
    print("VALIDATION INSPECTION COMPLETED")
    print("=" * 65)

    print("\nDataset shapes:")
    print("Yoga:", yoga_df.shape)
    print("Workout:", workout_df.shape)
    print("Gym Members:", gym_df.shape)


if __name__ == "__main__":
    main()
