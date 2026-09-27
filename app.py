import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Fertilizer Optimization Recommender",
    page_icon="🌱",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f7f9fc;
}

.title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    font-size: 18px;
    color: #666;
    margin-bottom: 30px;
}

.card {
    padding: 22px;
    border-radius: 15px;
    background-color: white;
    box-shadow: 0px 3px 12px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

.recommendation {
    padding: 20px;
    border-radius: 14px;
    background: linear-gradient(90deg, #dff7e7, #e8fff1);
    border-left: 6px solid #22a06b;
    font-size: 22px;
    font-weight: 600;
}

.info-box {
    padding: 16px;
    border-radius: 12px;
    background-color: #eef5ff;
    margin-top: 10px;
}

.footer {
    text-align: center;
    color: #777;
    margin-top: 40px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# FIND DATA FILE
# ============================================================

BASE_DIR = Path(__file__).parent

dataset_path = BASE_DIR / "data" / "fertilizer_recommendation.csv"

if not dataset_path.exists():
    st.error(
        "❌ fertilizer_recommendation.csv was not found inside the data folder."
    )
    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = pd.read_csv(dataset_path)
except Exception as e:
    st.error(f"❌ Could not read the dataset: {e}")
    st.stop()


# Remove completely empty rows/columns
df = df.dropna(how="all")
df = df.dropna(axis=1, how="all")


# Clean column names
df.columns = [str(col).strip() for col in df.columns]


# ============================================================
# HELPER FUNCTION TO FIND COLUMNS
# ============================================================

def find_column(possible_names):
    """
    Finds a column even if the exact capitalization/name differs.
    """

    normalized = {
        str(col).lower().replace(" ", "").replace("_", ""): col
        for col in df.columns
    }

    for name in possible_names:
        key = name.lower().replace(" ", "").replace("_", "")

        if key in normalized:
            return normalized[key]

    # Partial matching
    for col in df.columns:
        clean_col = str(col).lower().replace(" ", "").replace("_", "")

        for name in possible_names:
            clean_name = name.lower().replace(" ", "").replace("_", "")

            if clean_name in clean_col or clean_col in clean_name:
                return col

    return None


# ============================================================
# FIND IMPORTANT DATASET COLUMNS
# ============================================================

target_col = find_column([
    "Recommended_Fertilizer",
    "Recommended Fertilizer",
    "Fertilizer",
    "RecommendedFertilizer"
])

crop_col = find_column([
    "Crop",
    "Crop_Name",
    "CropName"
])

nitrogen_col = find_column([
    "Nitrogen_Level",
    "Nitrogen",
    "Nitrogen_N",
    "N"
])

phosphorus_col = find_column([
    "Phosphorus_Level",
    "Phosphorus",
    "Phosphorus_P",
    "P"
])

potassium_col = find_column([
    "Potassium_Level",
    "Potassium",
    "Potassium_K",
    "K"
])

ph_col = find_column([
    "Soil_pH",
    "SoilPH",
    "pH",
    "PH"
])


# ============================================================
# CHECK TARGET
# ============================================================

if target_col is None:

    st.error(
        "❌ I could not find the Recommended_Fertilizer column "
        "in your CSV file."
    )

    st.write("Columns found in your dataset:")
    st.write(list(df.columns))

    st.stop()


# ============================================================
# CLEAN TARGET
# ============================================================

df[target_col] = df[target_col].astype(str).str.strip()

df = df[
    (df[target_col].notna()) &
    (df[target_col] != "") &
    (df[target_col].str.lower() != "nan")
].copy()


# ============================================================
# PAGE TITLE
# ============================================================

st.markdown(
    '<div class="title">🌱 Fertilizer Optimization Recommender</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Enter your soil and crop information to get a machine-learning-based fertilizer recommendation.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# DATASET INFORMATION
# ============================================================

with st.expander("📊 Dataset Information"):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Records", len(df))

    with col2:
        st.metric("Total Columns", len(df.columns))

    with col3:
        st.metric("Fertilizer Classes", df[target_col].nunique())

    st.write("Dataset columns:")
    st.write(list(df.columns))


# ============================================================
# INPUT SECTION
# ============================================================

st.markdown("## 🌾 Enter Soil & Crop Information")


col1, col2 = st.columns(2)


# -------------------------
# CROP
# -------------------------

with col1:

    if crop_col is not None:

        crop_values = (
            df[crop_col]
            .dropna()
            .astype(str)
            .str.strip()
            .unique()
            .tolist()
        )

        crop_values = sorted(crop_values)

        if len(crop_values) > 0:

            crop = st.selectbox(
                "🌾 Select Crop",
                crop_values
            )

        else:

            crop = st.selectbox(
                "🌾 Select Crop",
                ["Wheat", "Rice", "Maize", "Cotton", "Sugarcane"]
            )

    else:

        crop = st.selectbox(
            "🌾 Select Crop",
            ["Wheat", "Rice", "Maize", "Cotton", "Sugarcane"]
        )


# -------------------------
# NITROGEN
# -------------------------

with col2:

    nitrogen = st.number_input(
        "🧪 Nitrogen (N)",
        min_value=0.0,
        max_value=300.0,
        value=50.0,
        step=1.0
    )


# -------------------------
# PHOSPHORUS
# -------------------------

col1, col2 = st.columns(2)

with col1:

    phosphorus = st.number_input(
        "🧪 Phosphorus (P)",
        min_value=0.0,
        max_value=300.0,
        value=50.0,
        step=1.0
    )


# -------------------------
# POTASSIUM
# -------------------------

with col2:

    potassium = st.number_input(
        "🧪 Potassium (K)",
        min_value=0.0,
        max_value=300.0,
        value=50.0,
        step=1.0
    )


# -------------------------
# SOIL PH
# -------------------------

col1, col2 = st.columns(2)

with col1:

    soil_ph = st.number_input(
        "🌱 Soil pH",
        min_value=0.0,
        max_value=14.0,
        value=6.5,
        step=0.1
    )


# -------------------------
# BUDGET
# -------------------------

with col2:

    budget = st.number_input(
        "💰 Fertilizer Budget (₹)",
        min_value=0.0,
        value=2000.0,
        step=100.0
    )


# ============================================================
# BUILD MODEL DATA
# ============================================================

# We use only the information that the user can actually enter.
# This prevents the old "median with string dtype" error.

feature_columns = []

if crop_col is not None:
    feature_columns.append(crop_col)

if nitrogen_col is not None:
    feature_columns.append(nitrogen_col)

if phosphorus_col is not None:
    feature_columns.append(phosphorus_col)

if potassium_col is not None:
    feature_columns.append(potassium_col)

if ph_col is not None:
    feature_columns.append(ph_col)


# Make sure we have enough features
if len(feature_columns) == 0:

    st.error(
        "❌ No usable input columns were found in the dataset."
    )

    st.write(list(df.columns))
    st.stop()


# ============================================================
# PREPARE TRAINING DATA
# ============================================================

X = df[feature_columns].copy()
y = df[target_col].copy()


# Identify categorical and numerical columns
categorical_features = X.select_dtypes(
    include=["object", "category"]
).columns.tolist()

numerical_features = X.select_dtypes(
    include=[np.number]
).columns.tolist()


# ============================================================
# PREPROCESSOR
# ============================================================

transformers = []


if len(categorical_features) > 0:

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent")
            ),
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore"
                )
            )
        ]
    )

    transformers.append(
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    )


if len(numerical_features) > 0:

    numerical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median")
            )
        ]
    )

    transformers.append(
        (
            "numerical",
            numerical_pipeline,
            numerical_features
        )
    )


preprocessor = ColumnTransformer(
    transformers=transformers,
    remainder="drop"
)


# ============================================================
# MACHINE LEARNING MODEL
# ============================================================

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight="balanced"
)


pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ============================================================
# TRAIN MODEL
# ============================================================

model_accuracy = None

try:

    # Check if stratified split is possible
    class_counts = y.value_counts()

    can_split = (
        len(y) >= 10
        and y.nunique() >= 2
        and class_counts.min() >= 2
    )

    if can_split:

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
            stratify=y
        )

        pipeline.fit(X_train, y_train)

        y_pred = pipeline.predict(X_test)

        model_accuracy = accuracy_score(
            y_test,
            y_pred
        )

    else:

        pipeline.fit(X, y)


except Exception as e:

    st.error(f"❌ Model training error: {e}")
    st.stop()


# ============================================================
# GET RECOMMENDATION BUTTON
# ============================================================

st.markdown("---")

get_recommendation = st.button(
    "🌱 Get Recommendation",
    type="primary",
    use_container_width=True
)


# ============================================================
# RECOMMENDATION
# ============================================================

if get_recommendation:

    # Create user's input
    user_input = {}

    if crop_col is not None:
        user_input[crop_col] = crop

    if nitrogen_col is not None:
        user_input[nitrogen_col] = nitrogen

    if phosphorus_col is not None:
        user_input[phosphorus_col] = phosphorus

    if potassium_col is not None:
        user_input[potassium_col] = potassium

    if ph_col is not None:
        user_input[ph_col] = soil_ph


    input_df = pd.DataFrame(
        [user_input],
        columns=feature_columns
    )


    # Predict
    try:

        prediction = pipeline.predict(input_df)

        recommended_fertilizer = str(
            prediction[0]
        ).strip()

    except Exception as e:

        st.error(
            f"❌ Could not generate recommendation: {e}"
        )

        st.stop()


    # ========================================================
    # SUCCESS MESSAGE
    # ========================================================

    st.success(
        "✅ Your soil information has been recorded!"
    )


    # ========================================================
    # YOUR INPUT
    # ========================================================

    st.markdown("## 📋 Your Input")


    input_col1, input_col2 = st.columns(2)


    with input_col1:

        st.write(f"🌾 **Crop:** {crop}")

        st.write(
            f"🧪 **Nitrogen:** {nitrogen:.1f}"
        )

        st.write(
            f"🧪 **Phosphorus:** {phosphorus:.1f}"
        )


    with input_col2:

        st.write(
            f"🧪 **Potassium:** {potassium:.1f}"
        )

        st.write(
            f"🌱 **Soil pH:** {soil_ph:.1f}"
        )

        st.write(
            f"💰 **Budget:** ₹{budget:.2f}"
        )


    # ========================================================
    # RECOMMENDATION
    # ========================================================

    st.markdown("## 🌱 Fertilizer Recommendation")


    st.markdown(
        f"""
        <div class="recommendation">
        🌱 Recommended Fertilizer: {recommended_fertilizer}
        </div>
        """,
        unsafe_allow_html=True
    )


    st.info(
        "This recommendation is generated using a "
        "Random Forest machine learning classification model "
        "trained on the provided fertilizer and soil dataset."
    )


    # ========================================================
    # MODEL ACCURACY
    # ========================================================

    if model_accuracy is not None:

        st.markdown("### 🤖 Model Performance")

        accuracy_col1, accuracy_col2 = st.columns(2)

        with accuracy_col1:

            st.metric(
                "Random Forest Accuracy",
                f"{model_accuracy * 100:.2f}%"
            )

        with accuracy_col2:

            st.metric(
                "Training Records",
                len(df)
            )


    # ========================================================
    # SUMMARY
    # ========================================================

    st.markdown("## 📊 Summary")


    summary1, summary2 = st.columns(2)


    with summary1:

        st.write(f"🌾 **Crop:** {crop}")

        st.write(
            f"🧪 **Nitrogen (N):** {nitrogen:.1f}"
        )

        st.write(
            f"🧪 **Phosphorus (P):** {phosphorus:.1f}"
        )


    with summary2:

        st.write(
            f"🧪 **Potassium (K):** {potassium:.1f}"
        )

        st.write(
            f"🌱 **Soil pH:** {soil_ph:.1f}"
        )

        st.write(
            f"💰 **Budget:** ₹{budget:.2f}"
        )


    # ========================================================
    # INPUT NPK CHART
    # ========================================================

    st.markdown("## 📈 Soil Nutrient Levels")


    nutrient_data = pd.DataFrame(
        {
            "Nutrient": [
                "Nitrogen",
                "Phosphorus",
                "Potassium"
            ],
            "Value": [
                nitrogen,
                phosphorus,
                potassium
            ]
        }
    )

    st.bar_chart(
        nutrient_data.set_index("Nutrient")
    )


    # ========================================================
    # BUDGET INFORMATION
    # ========================================================

    st.markdown("## 💰 Budget Information")


    if budget > 0:

        st.info(
            f"Your available fertilizer budget is "
            f"₹{budget:,.2f}."
        )


    # ========================================================
    # ABOUT RECOMMENDATION
    # ========================================================

    st.markdown("## 💡 About the Recommendation")


    st.write(
        "The machine learning model analyzes the provided "
        "soil and crop information and predicts the most "
        "suitable fertilizer from the fertilizer classes "
        "present in the training dataset."
    )

    st.write(
        "The system uses a Random Forest classification model "
        "with preprocessing for categorical and numerical data."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
    🌱 Fertilizer Optimization Recommender |
    Machine Learning Project
    </div>
    """,
    unsafe_allow_html=True
)