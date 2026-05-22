@echo off
echo [INFO] Checking and installing dependencies...
.venv\Scripts\python.exe -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [WARNING] .venv pip failed. Attempting global python pip...
    python -m pip install -r requirements.txt
)
echo [INFO] Starting Streamlit Web Application...
.venv\Scripts\python.exe -m streamlit run app.py
pause
