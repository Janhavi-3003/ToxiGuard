"""Loads the trained TF-IDF + KNN model and produces a full verdict for a message."""
import json
import os

import joblib
import sklearn

from nlp_utils import LANG_NAMES, clean_text, guess_language, lexicon_hits

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, "model")
VEC_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
KNN_PATH = os.path.join(MODEL_DIR, "knn_model.pkl")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")

MAX_LEN = 500


def _model_is_current():
    if not (os.path.exists(VEC_PATH) and os.path.exists(KNN_PATH) and os.path.exists(META_PATH)):
        return False
    try:
        with open(META_PATH, encoding="utf-8") as f:
            return json.load(f).get("sklearn") == sklearn.__version__
    except Exception:
        return False


class ToxiGuard:
    def __init__(self):
        if not _model_is_current():
            print("Model missing or built with another scikit-learn version -> training now ...")
            from train import train_and_save
            train_and_save(verbose=False)
        self.vectorizer = joblib.load(VEC_PATH)
        self.knn = joblib.load(KNN_PATH)
        self.toxic_idx = list(self.knn.classes_).index(1)

    def predict(self, text):
        text = (text or "").strip()[:MAX_LEN]
        cleaned = clean_text(text)
        hits, votes = lexicon_hits(text)
        lang = guess_language(text, votes)

        knn_score = 0.0
        if cleaned:
            X = self.vectorizer.transform([text])
            knn_score = float(self.knn.predict_proba(X)[0][self.toxic_idx])
            nearest = float(self.knn.kneighbors(X, n_neighbors=1)[0][0][0])   # cosine distance
            if nearest > 0.85 and not hits:      # message looks like nothing we trained on
                knn_score = min(knn_score, 0.25)

        score = knn_score
        if hits:
            score = max(knn_score, min(1.0, 0.78 + 0.08 * (len(hits) - 1)))
        pct = round(score * 100, 1)

        if pct >= 80:
            level, action, mood = "Highly Toxic", "blocked", "toxic"
        elif pct >= 50:
            level, action, mood = "Toxic", "blocked", "toxic"
        elif pct >= 30:
            level, action, mood = "Borderline", "warned", "warn"
        else:
            level, action, mood = "Polite / Safe", "allowed", "polite"

        return {
            "prediction": 1 if pct >= 50 else 0,
            "label": "Toxic" if pct >= 50 else "Non-toxic",
            "toxicity_score": pct,
            "knn_score": round(knn_score * 100, 1),
            "level": level,
            "action": action,
            "mood": mood,
            "language": LANG_NAMES[lang],
            "lang_code": lang,
            "matched_words": sorted(set(hits)),
        }
