# ToxiGuard – Evil Guardian for Real-Time Toxicity Detection

Pipeline: **Dataset → Preprocessing → TF-IDF (word + char n-grams) → KNN → Flask API → HTML/CSS/JS chat UI**

Now multilingual: **English, Tamil, Telugu, Hindi** — including Roman-script mixing
(Tanglish, Tenglish, Hinglish) and common obfuscation like `st*pid`, `f@ck`, `idi0t`.

## What's new in this version
- **4 languages + code-mixing**: the model and a lexicon safety-net both understand
  native script (Tamil/Telugu/Hindi) and Roman-typed versions of the same languages.
- **Animated evil guardian**: the head **shakes "No"** and speaks the word "No" out loud
  (in the detected language) when a message is toxic. For polite messages, the guardian
  **nods and gives a thumbs-up**, silently.
- **Voice**: uses the browser's built-in Speech Synthesis (no API key, no internet
  needed after the page loads) — toggle it off any time with the "Voice replies" switch.
- **Live evil meter** showing the toxicity score, and a status dot showing whether the
  backend is reachable.

## Quick start (Windows)
1. Install Python 3.9+ (tick "Add Python to PATH").
2. Double-click `run.bat` (creates venv, installs packages, trains model if needed, starts server).
3. Open http://127.0.0.1:5000

## Manual start
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cd backend
python train.py      # trains + saves model, prints accuracy/F1/confusion matrix
python app.py         # then open http://127.0.0.1:5000
```
Linux/Mac: use `source venv/bin/activate` and `./run.sh`.

Flask serves the frontend too, so only ONE terminal is needed.

## Project structure
```
toxiguard/
├── backend/
│   ├── app.py             Flask API + serves frontend
│   ├── train.py           trains TF-IDF+KNN, compares vs Naive Bayes / Logistic Regression / SVM
│   ├── toxicity.py        loads the model, produces the full verdict (score/level/language/action)
│   ├── nlp_utils.py        cleaning, tokenizing, language detection, multilingual lexicon
│   ├── make_dataset.py     generates the multilingual starter dataset
│   ├── model/              knn_model.pkl, tfidf_vectorizer.pkl, model_meta.json
│   └── dataset/toxic_comments.csv   (text,label   0=non-toxic 1=toxic)
├── frontend/   index.html, style.css, app.js
├── requirements.txt, run.bat, run.sh
```

## Important — before your final submission
The included dataset (~1700 template-based rows across 4 languages) demonstrates the
pipeline end-to-end but is not a substitute for real data. For your final project:
1. Replace `backend/dataset/toxic_comments.csv` with a real labeled dataset (e.g. Kaggle
   "Jigsaw Toxic Comment Classification" for English; add Tamil/Telugu/Hindi toxic-comment
   sets if your report requires them), keeping the `text,label` format.
2. Re-run `python train.py`. It automatically re-trains, re-evaluates and re-saves the model.
3. `train.py` already prints a comparison table of **KNN vs Naive Bayes vs Logistic
   Regression vs SVM** — use it directly in your report.

## API
```
POST /predict   {"text": "You are stupid"}
```
```json
{
  "prediction": 1,
  "label": "Toxic",
  "toxicity_score": 100.0,
  "knn_score": 91.2,
  "level": "Highly Toxic",
  "action": "blocked",
  "mood": "toxic",
  "language": "English",
  "lang_code": "en",
  "matched_words": ["stupid"]
}
```
`mood` drives the frontend animation/voice: `toxic` (shake head + say "No"),
`warn` (small shake, no voice by default), `polite` (nod + thumbs-up, silent).

## Notes on the multilingual detector
- **Two-layer approach**: a TF-IDF+KNN model trained on ~1700 multilingual examples,
  plus a hand-built lexicon of known abusive words/phrases in all 4 languages (native
  script + Roman script) as a safety net — agglutinative languages like Tamil/Telugu/
  Hindi get many word endings that a small ML dataset alone won't cover.
- **Language shown in the UI** is guessed from Unicode script first, then from common
  Roman-script words (e.g. "poda", "nuvvu", "bewakoof") if the text is typed in English
  letters.
- Voice uses the browser's `speechSynthesis` API with `lang` set to `ta-IN` / `te-IN` /
  `hi-IN` / `en-IN`; available voices/quality depend on the OS and browser (Chrome/Edge
  on Windows generally have the best Indian-language voice coverage).
