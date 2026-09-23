"""
This file defines our tf-idf representation of the free text "charge" column, then uses that representation to perform a logistic regression which
predicts the "category" of a crime based on its charge description.
Our model uses a 70% train, 15% validation, %15 test split.
During the validation phase, we use 5-fold cross validation to test C parameters [0.01, 0.1, 1, 10, 100] for the logistic regression to learn the best (most accurate and generalizable) C.
The model then uses the learned parameter to run on the test data, and outputs accuracy metrics.
"""

import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


#df = pd.read_csv("../DATA/model_training_data.csv") #CHANGE THIS TO OUR ACTUAL PREPROCESSED DATA
df = pd.read_csv("../DATA/mock_model_training_data.csv")#CHANGE THIS TO OUR ACTUAL PREPROCESSED DATA
df = df.dropna(subset=["Charge", "Category"])

X = df["Charge"]
y = df["Category"]

X_train_val, X_test, y_train_val, y_test = train_test_split(
    X,
    y,
    test_size=0.15,
    stratify=y,
    random_state=42
)

X_train, X_val, y_train, y_val = train_test_split(
    X_train_val,
    y_train_val,
    test_size=0.1765,
    stratify=y_train_val,
    random_state=42
)

model = Pipeline([
    ("tfidf", TfidfVectorizer(
        lowercase=True,
        stop_words="english" #might have to change this later
    )),
    ("logreg", LogisticRegression(
        max_iter=1000
    ))
])

param_grid = {
    "logreg__C": [0.01, 0.1, 1, 10, 100]
}

grid_search = GridSearchCV(
    model,
    param_grid,
    cv=5,
    scoring="accuracy",
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print("Best parameters:")
print(grid_search.best_params_)

print("\nBest cross-validation accuracy:")
print(grid_search.best_score_)

best_model = grid_search.best_estimator_
y_val_pred = best_model.predict(X_val)

print("\nValidation accuracy:")
print(accuracy_score(y_val, y_val_pred))

print("\nValidation classification report:")
print(classification_report(y_val, y_val_pred))

#Actually apply the model to the test data
y_test_pred = best_model.predict(X_test)

print("\nTest accuracy:")
print(accuracy_score(y_test, y_test_pred))

print("\nTest classification report:")
print(classification_report(y_test, y_test_pred))