# knn_patient_classification.py
import pandas as pd
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)

# === Load dataset ===
file_path = os.path.join(BASE_DIR, "TrainingDataset.xlsx")
data = pd.read_excel(file_path, sheet_name="PCTrainingDataset")

# === Separate features and target ===
X = data.drop(columns=["Result"])
y = data["Result"]

# === Encode categorical variables ===
categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()
le_dict = {}
for col in categorical_cols:
    le = LabelEncoder()
    X[col] = X[col].astype(str)
    X[col] = le.fit_transform(X[col])
    le_dict[col] = le

# === Handle missing values ===
imputer_num = SimpleImputer(strategy="mean")
imputer_cat = SimpleImputer(strategy="most_frequent")

numeric_cols = X.select_dtypes(include=["float64", "int64"]).columns.tolist()

X[numeric_cols] = imputer_num.fit_transform(X[numeric_cols])
X[categorical_cols] = imputer_cat.fit_transform(X[categorical_cols])

# === Feature scaling ===
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === Train/test split ===
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# === Build KNN classifier ===
knn = KNeighborsClassifier(
    n_neighbors=5,
    weights="distance",
    metric="minkowski"
)

start_train = time.time()
knn.fit(X_train, y_train)
end_train = time.time()

start_pred = time.time()
y_pred = knn.predict(X_test)
end_pred = time.time()

# === Evaluation ===
acc = accuracy_score(y_test, y_pred)
print("KNN Classifier Performance")
print(f"Accuracy: {acc:.4f}")
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("Classification Report:\n", classification_report(y_test, y_pred))
print(f"Training Time: {end_train - start_train:.4f}s | Prediction Time: {end_pred - start_pred:.4f}s")

os.makedirs("models", exist_ok=True)


metrics = {
    "accuracy": round(acc * 100, 2),
    "correct_pct": round(((y_test == y_pred).sum() / len(y_test)) * 100, 2),
    "incorrect_pct": round(((y_test != y_pred).sum() / len(y_test)) * 100, 2),
    "training_time": round(end_train - start_train, 4),
    "prediction_time": round((end_pred - start_pred) * 1000, 2),
    "test_samples": len(y_test),
    "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
}


report = classification_report(
    y_test,
    y_pred,
    output_dict=True
)


# === Save dropdown choices for Flask ===
categorical_choices = {}

for col in categorical_cols:
    categorical_choices[col] = sorted(
        data[col].dropna().astype(str).unique().tolist()
    )


# === Save model and preprocessing objects ===
joblib.dump(metrics, os.path.join(MODEL_DIR, "knn_metrics.pkl"))

joblib.dump(report, os.path.join(MODEL_DIR, "classification_report.pkl"))

joblib.dump(categorical_choices, os.path.join(MODEL_DIR, "categorical_choices.pkl"))

joblib.dump(knn, os.path.join(MODEL_DIR, "knn_model.pkl"))

joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

joblib.dump(le_dict, os.path.join(MODEL_DIR, "label_encoders.pkl"))

joblib.dump(imputer_num, os.path.join(MODEL_DIR, "imputer_num.pkl"))

joblib.dump(imputer_cat, os.path.join(MODEL_DIR, "imputer_cat.pkl"))

joblib.dump(X.columns.tolist(), os.path.join(MODEL_DIR, "feature_names.pkl"))

joblib.dump(categorical_cols, os.path.join(MODEL_DIR, "categorical_cols.pkl"))

joblib.dump(numeric_cols, os.path.join(MODEL_DIR, "numeric_cols.pkl"))