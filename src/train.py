"""Train the fraud classifiers compared in notebook 03."""

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.features import MODEL_FEATURES

RANDOM_STATE = 42


def split_data(df, test_size=0.3):
    """Stratified split so train and test keep the same fraud rate."""
    X = df[MODEL_FEATURES]
    y = df["Class"]
    return train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=RANDOM_STATE
    )


def build_models():
    """Four models, from simplest to most advanced.

    SMOTE sits inside an imblearn pipeline, so synthetic fraud cases are
    only ever created from training data - never from the test set.
    """
    return {
        "Logistic Regression (baseline)": Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000)),
        ]),
        "Logistic Regression (class-weighted)": Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]),
        "Logistic Regression (SMOTE)": ImbPipeline([
            ("scale", StandardScaler()),
            ("smote", SMOTE(random_state=RANDOM_STATE)),
            ("model", LogisticRegression(max_iter=1000)),
        ]),
        "Random Forest (class-weighted)": RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=5,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


def train_models(X_train, y_train):
    """Fit every model and return them in a dictionary."""
    models = build_models()
    for name, model in models.items():
        print(f"Training {name} ...")
        model.fit(X_train, y_train)
    return models
