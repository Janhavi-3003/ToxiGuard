@echo off
cd /d "%~dp0"
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)
cd backend
if not exist model\knn_model.pkl python train.py
python app.py
pause
