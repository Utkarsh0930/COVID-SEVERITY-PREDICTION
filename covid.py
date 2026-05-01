import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay
)
import joblib


BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "Covid_dataset_curated.xlsx"


df = pd.read_excel(DATA_PATH)
print(df.info())

TARGET_COLUMN = "severity"

label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df[TARGET_COLUMN])

X = df.drop(TARGET_COLUMN, axis=1)
X = pd.get_dummies(X)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

base_estimator = DecisionTreeClassifier(max_depth=1)

adaboost_model = AdaBoostClassifier(
    estimator=base_estimator,
    n_estimators=300,
    learning_rate=0.5,
    random_state=42
)
adaboost_model.fit(X_train, y_train)

y_pred = adaboost_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"Test Accuracy: {accuracy:.4f}")

print("\nClassification Report:\n")
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:\n", cm)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(adaboost_model, X, y, cv=cv, scoring="accuracy")
print(f"\n5-Fold CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

importances = adaboost_model.feature_importances_
feature_importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

print("\nTop 10 Important Features:\n")
print(feature_importance_df.head(10))

plt.figure()
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=label_encoder.classes_)
disp.plot()
plt.title("AdaBoost Confusion Matrix — COVID Severity")
plt.tight_layout()
plt.show()

train_acc = []
test_acc = []

for y_train_pred in adaboost_model.staged_predict(X_train):
    train_acc.append(accuracy_score(y_train, y_train_pred))

for y_test_pred in adaboost_model.staged_predict(X_test):
    test_acc.append(accuracy_score(y_test, y_test_pred))

plt.figure(figsize=(8, 5))
plt.plot(range(1, len(train_acc) + 1), train_acc, label="Training Accuracy")
plt.plot(range(1, len(test_acc) + 1), test_acc, label="Testing Accuracy")
plt.xlabel("Number of Estimators")
plt.ylabel("Accuracy")
plt.title("AdaBoost Performance vs Number of Estimators")
plt.legend()
plt.tight_layout()
plt.show()

joblib.dump(adaboost_model,           BASE_DIR / "adaboost_covid_model.joblib")
joblib.dump(label_encoder,            BASE_DIR / "label_encoder.joblib")
joblib.dump(X.columns.tolist(),       BASE_DIR / "feature_columns.joblib")
print("\nModel and artifacts saved successfully.")