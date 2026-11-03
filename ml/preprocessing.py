
import json
import re
from pathlib import Path

import pandas as pd

from config import (
    YOGA_FILE,
    EXERCISEDB_FILE,
    GYM_MEMBERS_FILE,
    PROCESSED_DIR,
    CLEANED_YOGA_FILE,
    CLEANED_WORKOUT_FILE,
    CLEANED_GYM_FILE,
    DUPLICATE_REPORT_FILE,
)


def load_json_records(file_path):
    """Load JSON records from either a list or a dictionary."""
    if not file_path.exists():
        raise FileNotFoundError(f"Dataset not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # Support common dictionary wrappers around record lists.
        for key in ("data", "exercises", "yoga", "poses", "results"):
            if isinstance(data.get(key), list):
                return data[key]

        return [data]

    raise ValueError(f"Unsupported JSON structure in {file_path.name}")


def get_value(record, *keys, default=""):
    """Return the first available non-empty field."""
    for key in keys:
        value = record.get(key)

        if value is not None and value != "":
            return value

    return default


def get_english_text(value):
    """Extract English text from localized instruction fields."""
    if isinstance(value, dict):
        return value.get("en", "")

    if isinstance(value, str):
        return value

    return ""


def to_text(value):
    """Convert lists and dictionaries into readable CSV-safe text."""
    if value is None:
        return ""

    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False)

    return str(value)


def extract_yoga_data():
    records = load_json_records(YOGA_FILE)
    cleaned = []

    for record in records:
        if not isinstance(record, dict):
            continue

        cleaned.append({
            "id": get_value(record, "id"),
            "name": get_value(record, "name"),
            "sanskrit_name": get_value(record, "sanskrit_name"),
            "category": to_text(get_value(record, "category")),
            "categories": to_text(get_value(record, "categories")),
            "difficulty": get_value(record, "difficulty"),
            "focus": to_text(get_value(record, "focus")),
            "target_areas": to_text(get_value(record, "target_areas")),
            "description": get_value(record, "description"),
            "benefits": to_text(get_value(record, "benefits")),
            "instructions": to_text(
                get_value(record, "instruction_steps")
            ),
            "image": get_value(record, "image"),
            "svg": get_value(record, "svg"),
        })

    return pd.DataFrame(cleaned)


def extract_workout_data():
    records = load_json_records(EXERCISEDB_FILE)
    cleaned = []

    for record in records:
        if not isinstance(record, dict):
            continue

        cleaned.append({
            "id": get_value(record, "id"),
            "name": get_value(record, "name"),
            "category": get_value(record, "category"),
            "body_part": get_value(record, "body_part"),
            "equipment": get_value(record, "equipment"),
            "instructions": get_english_text(
                get_value(record, "instructions")
            ),
            "instruction_steps": to_text(
                get_english_text(
                    get_value(record, "instruction_steps")
                )
            ),
            "image": get_value(
                record, "image", "image_url", "gifUrl"
            ),
            "video": get_value(
                record, "video", "video_url"
            ),
        })

    return pd.DataFrame(cleaned)


def clean_gym_members_data():
    if not GYM_MEMBERS_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {GYM_MEMBERS_FILE}"
        )

    df = pd.read_csv(GYM_MEMBERS_FILE)

    # Standardize column names for easier use in Python.
    df.columns = [
        re.sub(
            r"_+",
            "_",
            re.sub(
                r"[^a-zA-Z0-9]+",
                "_",
                column.strip()
            )
        ).strip("_").lower()
        for column in df.columns
    ]

    # Remove fully duplicated rows, but keep all other records.
    df = df.drop_duplicates()

    return df


def create_duplicate_report(yoga_df, workout_df):
    """Report repeated names; do not automatically delete them."""
    rows = []

    for dataset_name, df in (
        ("yoga", yoga_df),
        ("workout", workout_df),
    ):
        if "name" not in df.columns:
            continue

        names = df["name"].fillna("").astype(str).str.strip()
        normalized = names.str.lower()

        for name in normalized[normalized.duplicated(keep=False)].unique():
            matching = names[normalized == name].tolist()

            rows.append({
                "dataset": dataset_name,
                "normalized_name": name,
                "matching_names": " | ".join(matching),
                "occurrences": len(matching),
            })

    report = pd.DataFrame(
        rows,
        columns=[
            "dataset",
            "normalized_name",
            "matching_names",
            "occurrences",
        ],
    )

    report.to_csv(DUPLICATE_REPORT_FILE, index=False)


def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Starting FitFlow AI dataset preprocessing...\n")

    yoga_df = extract_yoga_data()
    workout_df = extract_workout_data()
    gym_df = clean_gym_members_data()

    yoga_df.to_csv(CLEANED_YOGA_FILE, index=False, encoding="utf-8-sig")
    workout_df.to_csv(
        CLEANED_WORKOUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )
    gym_df.to_csv(CLEANED_GYM_FILE, index=False, encoding="utf-8-sig")

    create_duplicate_report(yoga_df, workout_df)

    print("Preprocessing completed successfully!\n")
    print(f"Yoga poses: {len(yoga_df)}")
    print(f"Workout exercises: {len(workout_df)}")
    print(f"Gym member records: {len(gym_df)}")

    print("\nMissing values:")
    print(f"Yoga: {yoga_df.isnull().sum().sum()}")
    print(f"Workout: {workout_df.isnull().sum().sum()}")
    print(f"Gym: {gym_df.isnull().sum().sum()}")

    print("\nCleaned files saved in:")
    print(PROCESSED_DIR)


if __name__ == "__main__":
    main()
