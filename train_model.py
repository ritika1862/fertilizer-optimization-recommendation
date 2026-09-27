import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# -----------------------------------
# 1. LOAD DATASET
# -----------------------------------

file_path = "data/fertilizer_recommendation.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


# -----------------------------------
# 2. SEPARATE INPUT AND TARGET
# -----------------------------------

target = "Recommended_Fertilizer"

X = df.drop(columns=[target])
y = df[target]

print("\nTarget column:", target)
print("Number of fertilizer classes:", y.nunique())

print("\nFertilizer classes:")
print(y.unique())


# -----------------------------------
# 3. IDENTIFY COLUMN TYPES
# -----------------------------------

categorical_columns = X.select_dtypes(
    include=["object"]
).columns.tolist()

numerical_columns = X.select_dtypes(
    exclude=["object"]
).columns.tolist()

print("\nCategorical columns:")
print(categorical_columns)

print("\nNumerical columns:")
print(numerical_columns)


# -----------------------------------
# 4. PREPROCESSING
# -----------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_columns
        ),
        (
            "numerical",
            "passthrough",
            numerical_columns
        )
    ]
)


# -----------------------------------
# 5. MACHINE LEARNING MODEL
# -----------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)


# -----------------------------------
# 6. CREATE ML PIPELINE
# -----------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# -----------------------------------
# 7. TRAIN / TEST SPLIT
# -----------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# -----------------------------------
# 8. TRAIN MODEL
# -----------------------------------

print("\nTraining Random Forest model...")

pipeline.fit(X_train, y_train)

print("Model training completed!")


# -----------------------------------
# 9. EVALUATE MODEL
# -----------------------------------

y_pred = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n-----------------------------------")
print("MODEL PERFORMANCE")
print("-----------------------------------")

print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# -----------------------------------
# 10. TEST ONE PREDICTION
# -----------------------------------

sample = X_test.iloc[[0]]

prediction = pipeline.predict(sample)

print("\n-----------------------------------")
print("SAMPLE PREDICTION")
print("-----------------------------------")

print("Predicted fertilizer:", prediction[0])
print("Actual fertilizer:", y_test.iloc[0])
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# -----------------------------------
# 1. LOAD DATASET
# -----------------------------------

file_path = "data/fertilizer_recommendation.csv"

df = pd.read_csv(file_path)

print("Dataset loaded successfully!")
print("Rows:", df.shape[0])
print("Columns:", df.shape[1])


# -----------------------------------
# 2. SEPARATE INPUT AND TARGET
# -----------------------------------

target = "Recommended_Fertilizer"

X = df.drop(columns=[target])
y = df[target]

print("\nTarget column:", target)
print("Number of fertilizer classes:", y.nunique())

print("\nFertilizer classes:")
print(y.unique())


# -----------------------------------
# 3. IDENTIFY COLUMN TYPES
# -----------------------------------

categorical_columns = X.select_dtypes(
    include=["object"]
).columns.tolist()

numerical_columns = X.select_dtypes(
    exclude=["object"]
).columns.tolist()

print("\nCategorical columns:")
print(categorical_columns)

print("\nNumerical columns:")
print(numerical_columns)


# -----------------------------------
# 4. PREPROCESSING
# -----------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_columns
        ),
        (
            "numerical",
            "passthrough",
            numerical_columns
        )
    ]
)


# -----------------------------------
# 5. MACHINE LEARNING MODEL
# -----------------------------------

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)


# -----------------------------------
# 6. CREATE ML PIPELINE
# -----------------------------------

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# -----------------------------------
# 7. TRAIN / TEST SPLIT
# -----------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# -----------------------------------
# 8. TRAIN MODEL
# -----------------------------------

print("\nTraining Random Forest model...")

pipeline.fit(X_train, y_train)

print("Model training completed!")


# -----------------------------------
# 9. EVALUATE MODEL
# -----------------------------------

y_pred = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n-----------------------------------")
print("MODEL PERFORMANCE")
print("-----------------------------------")

print("Accuracy:", round(accuracy * 100, 2), "%")

print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# -----------------------------------
# 10. TEST ONE PREDICTION
# -----------------------------------

sample = X_test.iloc[[0]]

prediction = pipeline.predict(sample)

print("\n-----------------------------------")
print("SAMPLE PREDICTION")
print("-----------------------------------")

print("Predicted fertilizer:", prediction[0])
print("Actual fertilizer:", y_test.iloc[0])
print("\nSaving model...")

joblib.dump(pipeline, "fertilizer_model.pkl")

print("Model saved successfully!")
print("File: fertilizer_model.pkl")