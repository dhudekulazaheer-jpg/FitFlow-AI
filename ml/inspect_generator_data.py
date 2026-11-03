
import json
from collections import Counter

from config import YOGA_FILE, EXERCISEDB_FILE


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    yoga_data = load_json(YOGA_FILE)
    exercise_data = load_json(EXERCISEDB_FILE)

    print("=" * 55)
    print("FITFLOW AI - GENERATOR DATA INSPECTION")
    print("=" * 55)

    print("\n1. YOGA DATA")
    print("-" * 45)

    print("Total poses:", len(yoga_data))

    print("\nDifficulty levels:")
    print(Counter(
        item.get("difficulty", "Unknown")
        for item in yoga_data
    ))

    print("\nYoga focus areas:")
    print(Counter(
        item.get("focus", "Unknown")
        for item in yoga_data
    ))

    print("\nYoga categories:")
    print(Counter(
        category
        for item in yoga_data
        for category in item.get("categories", [])
    ))

    print("\n2. WORKOUT DATA")
    print("-" * 45)

    print("Total exercises:", len(exercise_data))

    print("\nBody parts:")
    print(Counter(
        item.get("body_part", "Unknown")
        for item in exercise_data
    ))

    print("\nEquipment:")
    print(Counter(
        item.get("equipment", "Unknown")
        for item in exercise_data
    ))

    print("\nExercise categories:")
    print(Counter(
        item.get("category", "Unknown")
        for item in exercise_data
    ))

    print("\n3. SAMPLE FIELD AVAILABILITY")
    print("-" * 45)

    for label, dataset in [
        ("Yoga", yoga_data),
        ("Workout", exercise_data)
    ]:
        print(f"\n{label}:")

        if dataset:
            for key, value in dataset[0].items():
                print(f"{key}: {type(value).__name__}")

    print("\n" + "=" * 55)
    print("INSPECTION COMPLETED!")
    print("=" * 55)


if __name__ == "__main__":
    main()
