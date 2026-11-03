
import joblib
import pandas as pd

from config import MODEL_DIR

MODEL_PATH = MODEL_DIR / "calorie_regressor.pkl"

def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Trained model not found.")

    model = joblib.load(MODEL_PATH)

    print("=" * 45)
    print("FITFLOW AI - CALORIE PREDICTION TEST")
    print("=" * 45)

    age = int(input("Enter age: "))
    gender = input("Enter gender (Male/Female): ").strip().title()
    weight = float(input("Enter weight in kg: "))
    height = float(input("Enter height in metres: "))
    experience = int(input("Experience (1=Beginner, 2=Intermediate, 3=Advanced): "))
    frequency = int(input("Workout frequency per week (1-7): "))
    duration = float(input("Session duration in hours: "))
    workout_type = input("Workout type (Yoga/Cardio/Strength/HIIT): ").strip().title()

    user_data = pd.DataFrame([{
        "age": age,
        "gender": gender,
        "weight_kg": weight,
        "height_m": height,
        "experience_level": experience,
        "workout_frequency_days_week": frequency,
        "session_duration_hours": duration,
        "workout_type": workout_type
    }])

    prediction = model.predict(user_data)[0]

    print("\n" + "=" * 45)
    print("CALORIE PREDICTION RESULT")
    print("=" * 45)
    print(f"Estimated calories: {prediction:.2f} kcal")
    print("\nNote: This is a dataset-based estimate,")
    print("not a medically verified calorie measurement.")
    print("=" * 45)


if __name__ == "__main__":
    main()
