"""
Training script:  Dataset -> Preprocessing -> TF-IDF (word + char n-grams) -> KNN.
Also compares KNN with Naive Bayes, Logistic Regression and SVM (needed for the report).

Run:  python train.py
"""
import json
import os
import sys

import joblib
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from nlp_utils import clean_text, tokenize

BASE = os.path.dirname(os.path.abspath(__file__))
DATASET = os.path.join(BASE, "dataset", "toxic_comments.csv")
MODEL_DIR = os.path.join(BASE, "model")


def make_features():
    word = TfidfVectorizer(preprocessor=clean_text, tokenizer=tokenize, token_pattern=None,
                           lowercase=False, ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    char = TfidfVectorizer(preprocessor=clean_text, analyzer="char_wb", lowercase=False,
                           ngram_range=(2, 5), sublinear_tf=True, min_df=1)
    return FeatureUnion([("word", word), ("char", char)])


def make_knn():
    return KNeighborsClassifier(n_neighbors=5, weights="distance", metric="cosine", algorithm="brute")


HAND_TEST = [
    ("You are such an idiot", 1), ("shut up you moron", 1), ("I hate you so much", 1),
    ("what a pathetic loser", 1), ("you're a worthless piece of shit", 1),
    ("nobody wants you here, get lost", 1), ("I will find you and hurt you", 1),
    ("u r so dumb lol", 1), ("st*pid id!ot", 1), ("YOU ARE SO STUUUPID", 1),
    ("நீ சரியான மடையன்டா", 1), ("வாயை மூடு டா", 1), ("நீ எல்லாம் ஒரு லூசு", 1),
    ("dei loosu naaye poda", 1), ("nee oru waste fellow da", 1), ("unna kolla poren", 1),
    ("నువ్వు పెద్ద వెధవవి", 1), ("నోరు మూసుకో దద్దమ్మ", 1), ("నిన్ను చంపేస్తా", 1),
    ("nuvvu oka vedhava ra", 1), ("noru musuko", 1),
    ("तू बहुत बड़ा बेवकूफ है", 1), ("चुप कर कमीने", 1), ("मैं तुझे जान से मार दूँगा", 1),
    ("abe gadhe nikal yahan se", 1), ("tu ekdum ghatiya insaan hai", 1),
    ("Thank you for helping me today", 0), ("Have a great day my friend", 0),
    ("I disagree with your opinion but I respect it", 0), ("Could you please share the report?", 0),
    ("That movie was amazing", 0), ("The meeting starts at ten tomorrow", 0),
    ("Happy birthday, wishing you the best", 0), ("you are not stupid, you just need practice", 0),
    ("உங்கள் உதவிக்கு மிக்க நன்றி", 0), ("நாளை காலை சந்திப்போம்", 0),
    ("nandri nanba, romba help pannirukeenga", 0), ("vanakkam, eppadi irukeenga", 0),
    ("మీ సహాయానికి చాలా ధన్యవాదాలు", 0), ("రేపు ఉదయం కలుద్దాం", 0), ("meeru chala baga chepparu", 0),
    ("आपकी मदद के लिए बहुत धन्यवाद", 0), ("कल सुबह मिलते हैं", 0),
    ("aaj mausam bahut accha hai", 0), ("bhai tumne bahut badhiya kaam kiya", 0),
]


def train_and_save(verbose=True):
    if not os.path.exists(DATASET):
        from make_dataset import build
        import csv
        rows = build()
        os.makedirs(os.path.dirname(DATASET), exist_ok=True)
        with open(DATASET, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["text", "label"])
            w.writerows(rows)

    df = pd.read_csv(DATASET).dropna(subset=["text", "label"])
    df["label"] = df["label"].astype(int)
    X, y = df["text"].astype(str), df["label"]
    if verbose:
        print(f"Rows: {len(df)}   toxic: {int(y.sum())}   non-toxic: {int((y == 0).sum())}")

    if verbose:
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        knn_pipe = Pipeline([("tfidf", make_features()), ("clf", make_knn())])
        knn_pipe.fit(X_tr, y_tr)
        pred = knn_pipe.predict(X_te)
        print(f"\nKNN test accuracy: {accuracy_score(y_te, pred):.4f}")
        print("\nClassification report:")
        print(classification_report(y_te, pred, target_names=["Non-toxic", "Toxic"]))
        print("Confusion matrix:")
        print(confusion_matrix(y_te, pred))

        cv = cross_val_score(Pipeline([("tfidf", make_features()), ("clf", make_knn())]),
                             X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42), scoring="f1")
        print(f"\n5-fold cross-validation F1 (KNN): {cv.mean():.4f} +/- {cv.std():.4f}")

        print("\nModel comparison (same features, same split):")
        print(f"{'Model':<22}{'Accuracy':>10}{'F1':>10}")
        candidates = {
            "KNN (deployed)": make_knn(),
            "Naive Bayes": MultinomialNB(),
            "Logistic Regression": LogisticRegression(max_iter=1000),
            "SVM (LinearSVC)": LinearSVC(),
        }
        for name, clf in candidates.items():
            p = Pipeline([("tfidf", make_features()), ("clf", clf)]).fit(X_tr, y_tr).predict(X_te)
            print(f"{name:<22}{accuracy_score(y_te, p):>10.4f}{f1_score(y_te, p):>10.4f}")

    vectorizer = make_features()
    Xv = vectorizer.fit_transform(X)
    knn = make_knn().fit(Xv, y)
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl"))
    joblib.dump(knn, os.path.join(MODEL_DIR, "knn_model.pkl"))
    with open(os.path.join(MODEL_DIR, "model_meta.json"), "w", encoding="utf-8") as f:
        json.dump({"sklearn": sklearn.__version__, "rows": len(df)}, f)
    if verbose:
        print("\nModel saved successfully.")


def evaluate_full_system():
    from toxicity import ToxiGuard
    guard = ToxiGuard()
    right, wrong = 0, []
    for text, label in HAND_TEST:
        r = guard.predict(text)
        if r["prediction"] == label:
            right += 1
        else:
            wrong.append((text, label, r["toxicity_score"]))
    print(f"\nUnseen hand-written test (KNN + lexicon, 4 languages): {right}/{len(HAND_TEST)} correct "
          f"({100 * right / len(HAND_TEST):.1f}%)")
    for text, label, score in wrong:
        print(f"  missed: {text!r}  expected={'toxic' if label else 'safe'}  score={score}")


if __name__ == "__main__":
    train_and_save(verbose=True)
    evaluate_full_system()
    sys.exit(0)
