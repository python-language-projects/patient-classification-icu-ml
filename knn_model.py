# knn_patient_classification.py
import pandas as pd
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# === Load dataset ===
file_path = "TrainingDataset.xlsx"
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
knn = KNeighborsClassifier(n_neighbors=5)

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

# === Save model and preprocessing objects ===
joblib.dump(knn, "knn_model.pkl")
joblib.dump(scaler, "scaler.pkl")
joblib.dump(le_dict, "label_encoders.pkl")
joblib.dump(imputer_num, "imputer_num.pkl")
joblib.dump(imputer_cat, "imputer_cat.pkl")

# Save column info
joblib.dump(X.columns.tolist(), "feature_names.pkl")
joblib.dump(categorical_cols, "categorical_cols.pkl")
joblib.dump(numeric_cols, "numeric_cols.pkl")
